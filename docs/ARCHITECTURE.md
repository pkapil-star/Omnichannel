<!-- Omnichannel AI Support Agent for Local Businesses — Tech stack and workflow architecture -->

# Architecture

## System Architecture Overview

Hybrid 3-branch decision flow:

1. **Message In** → Azure Container Apps (webhook) → Service Bus → Classify + RAG
2. **Branch A** (FAQ + high confidence + non-negative sentiment): Gemini → Azure Function → Auto-reply
3. **Branch B** (urgent / negative): FCM push notify → Owner replies
4. **Branch C** (low confidence / complex): Dashboard queue → Owner reviews and replies

## Tech Stack

Azure for Students (no card, $100 credit) is the cloud. Gemini (AI Studio key) is the ML API. Firebase is used only for owner login and web push, both on the free Spark plan.

| Layer | Technology |
|---|---|
| Channel webhooks (WhatsApp, Instagram, Gmail) | Azure Container Apps — receives and validates incoming webhook pushes |
| Message routing | Azure Service Bus (Standard tier, topics) — one topic per channel |
| Conversation state & message history | Azure Cosmos DB for NoSQL (free tier) |
| Intent & sentiment classification | Gemini via the `google-genai` SDK, structured JSON output |
| RAG match + confidence score | Gemini embeddings (768 dims) + Cosmos DB vector search |
| LLM reply/summary generation | Gemini via the `google-genai` SDK, AI Studio API key (`GEMINI_API_KEY`), behind one function so the provider can be swapped |
| Outbound auto-reply — gated | Azure Function → WhatsApp Cloud API / Instagram Graph API / Gmail API |
| Owner notifications (urgent/low-confidence) | Firebase Cloud Messaging (web push) |
| Owner login | Firebase Auth (Google sign-in, one allowed email); Functions verify the Firebase ID token |
| Owner dashboard | React/Next.js static export on Azure Static Web Apps; polls an Azure Functions HTTP API every 3–5 s |
| Gate log & analytics | Cosmos DB `gate_logs` container; KPIs and charts in the dashboard Analytics screen and the evaluation script |

## Confidence Gate Logic

Three conditions, evaluated in order. All three must pass for auto-reply to fire.

| # | Condition | If it fails |
|---|---|---|
| 1 | Intent class = FAQ | → Dashboard queue |
| 2 | Confidence score ≥ 0.85 | → Dashboard queue |
| 3 | Sentiment ≠ negative | → FCM push notify |

Every evaluation (pass or fail) is logged to the Cosmos DB `gate_logs` container with intent, confidence, sentiment, and channel.

## Data Flow Walkthrough

### Walkthrough A: High-confidence FAQ (all gates pass) → auto-reply

1. Customer sends "What time do you open on Sunday?" on WhatsApp.
2. WhatsApp pushes webhook to Container Apps; signature validated.
3. Container Apps publishes to the `whatsapp` Service Bus topic and writes the message to Cosmos DB.
4. Classifier returns intent = FAQ, sentiment = neutral.
5. RAG embeds the query, Cosmos DB vector search returns the top FAQ match with confidence 0.92.
6. Gate: FAQ ✓, 0.92 ≥ 0.85 ✓, sentiment ≠ negative ✓ → pass.
7. Gemini generates a reply grounded in the matched FAQ.
8. Gated Azure Function sends the reply via WhatsApp Cloud API; Cosmos DB and `gate_logs` updated.

### Walkthrough B: Complaint / negative → FCM push notify → owner replies

1. Customer sends "My order is wrong and nobody is answering!" on Gmail.
2. Container Apps ingests, publishes to the `gmail` topic, stores in Cosmos DB.
3. Classifier returns intent = complaint, sentiment = negative.
4. Gate fails (intent ≠ FAQ, sentiment = negative). No Gemini reply call, no auto-reply.
5. FCM push sent to owner's phone (target < 5 s).
6. Owner opens the dashboard, sees the conversation, replies personally.
7. Gate decision logged to `gate_logs`.

### Walkthrough C: Ambiguous / low-confidence → dashboard queue → owner reviews

1. Customer sends "Do you do the thing from last time?" on WhatsApp.
2. Ingested and classified: intent = FAQ, sentiment = neutral.
3. RAG best match confidence = 0.41.
4. Gate fails on condition 2 → message placed in the dashboard queue.
5. Owner reviews at their convenience and replies from the dashboard.
6. Gate decision logged to `gate_logs` (useful for tuning the threshold and finding FAQ gaps).

## Azure Services Diagram

```
 WhatsApp        Instagram         Gmail
    │                │               │
    └───────┬────────┴───────┬───────┘
            ▼                ▼
   ┌──────────────────────────────┐
   │ Container Apps (webhooks)    │── validate ──► Cosmos DB (messages)
   └──────────────┬───────────────┘
                  ▼
   ┌──────────────────────────────┐
   │ Service Bus (1 topic/channel)│
   └──────────────┬───────────────┘
                  ▼
   ┌──────────────────────────────┐
   │ Container Apps (classifier)  │
   │  • Gemini intent + sentiment │
   │  • Gemini embeddings         │
   │  • Cosmos DB vector search   │ FAQ match + confidence
   └──────────────┬───────────────┘
                  ▼
        ┌───────────────────┐        every decision
        │  CONFIDENCE GATE  │──────────────────────────► Cosmos DB gate_logs
        └───┬───────┬───────┘
   all pass │       │ negative / urgent          low confidence / complex
            ▼       ▼                                   ▼
   ┌────────────┐ ┌──────────────┐          ┌──────────────────────┐
   │ Gemini     │ │ FCM push     │          │ Dashboard queue      │
   │ reply      │ │ to owner     │          │ (Cosmos DB)          │
   └─────┬──────┘ └──────┬───────┘          └──────────┬───────────┘
         ▼               └──────────────┬──────────────┘
   ┌────────────┐                       ▼
   │ Azure Func │            ┌─────────────────────┐
   │ (gated     │            │ Owner dashboard     │
   │  send)     │◄───────────│ React/Next.js       │
   └─────┬──────┘ owner reply│ (Static Web Apps)   │
         ▼                   └─────────────────────┘
  WhatsApp Cloud API / Instagram Graph API / Gmail API
```

## Key Design Decisions

- **Container Apps for webhooks** — serverless, scales to zero, free monthly grant. Fits bursty, unpredictable webhook traffic from small businesses.
- **Service Bus, one topic per channel** — decouples ingestion from processing so webhooks can return fast; per-channel topics keep routing, retries, and failure isolation separate. Topics need the Standard tier (Basic has queues only), paid from student credit.
- **Cosmos DB** — JSON documents map onto conversation threads and varied channel payloads; native vector search keeps FAQ matching in one service. The free tier gives 1000 RU/s and 25 GB.
- **Polling instead of realtime listeners** — Cosmos has no `onSnapshot`. The dashboard polls every 3–5 s, which is enough for the demo. SignalR is the upgrade path.
- **Firebase kept for Auth and FCM only** — both are free on Spark without a card and have no Azure equivalent as simple.
- **Tunable confidence gate** — threshold lives in configuration, not code. Starts at 0.85 and is tuned from `gate_logs` data.
- **Gemini reply only after the gate passes** — messages routed to push or the dashboard never incur a reply-generation call, which controls cost and avoids generating replies that will never be sent.
- **One LLM call site** — the provider stays behind one function, so Gemini can move to Azure OpenAI later.
