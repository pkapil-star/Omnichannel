<!-- Omnichannel AI Support Agent for Local Businesses — Tech stack and workflow architecture -->

# Architecture

## System Architecture Overview

Hybrid 3-branch decision flow:

1. **Message In** → Cloud Run (webhook) → Pub/Sub → Classify + RAG
2. **Branch A** (FAQ + high confidence + non-negative sentiment): Gemini → Cloud Function → Auto-reply
3. **Branch B** (urgent / negative): FCM push notify → Owner replies
4. **Branch C** (low confidence / complex): Dashboard queue → Owner reviews and replies

## Tech Stack

| Layer | Technology |
|---|---|
| Channel webhooks (WhatsApp, Instagram, Gmail) | Cloud Run — receives and validates incoming webhook pushes |
| Message routing | Pub/Sub — one topic per channel |
| Conversation state & message history | Firestore |
| Intent & sentiment classification | Natural Language API (or Vertex AI AutoML Text) |
| RAG match + confidence score | Gemini embeddings (768 dims) + Firestore native vector search |
| LLM reply/summary generation | Gemini via AI Studio API key (behind one function, so a later Vertex AI switch is a one-place change) |
| Outbound auto-reply — gated | Cloud Function → WhatsApp Cloud API / Instagram Graph API / Gmail API |
| Owner notifications (urgent/low-confidence) | Firebase Cloud Messaging (push) |
| Owner dashboard | React/Next.js on Cloud Run or Firebase Hosting |
| Analytics | BigQuery + Looker Studio |

## Confidence Gate Logic

Three conditions, evaluated in order. All three must pass for auto-reply to fire.

| # | Condition | If it fails |
|---|---|---|
| 1 | Intent class = FAQ | → Dashboard queue |
| 2 | Confidence score ≥ 0.85 | → Dashboard queue |
| 3 | Sentiment ≠ negative | → FCM push notify |

Every evaluation (pass or fail) is logged to BigQuery with intent, confidence, sentiment, and channel.

## Data Flow Walkthrough

### Walkthrough A: High-confidence FAQ (all gates pass) → auto-reply

1. Customer sends "What time do you open on Sunday?" on WhatsApp.
2. WhatsApp pushes webhook to Cloud Run; signature validated.
3. Cloud Run publishes to the `whatsapp` Pub/Sub topic and writes the message to Firestore.
4. Classifier returns intent = FAQ, sentiment = neutral.
5. RAG embeds the query, Vector Search returns the top FAQ match with confidence 0.92.
6. Gate: FAQ ✓, 0.92 ≥ 0.85 ✓, sentiment ≠ negative ✓ → pass.
7. Gemini generates a reply grounded in the matched FAQ.
8. Gated Cloud Function sends the reply via WhatsApp Cloud API; Firestore and BigQuery updated.

### Walkthrough B: Complaint / negative → FCM push notify → owner replies

1. Customer sends "My order is wrong and nobody is answering!" on Gmail.
2. Cloud Run ingests, publishes to the `gmail` topic, stores in Firestore.
3. Classifier returns intent = complaint, sentiment = negative.
4. Gate fails (intent ≠ FAQ, sentiment = negative). No Gemini call, no auto-reply.
5. FCM push sent to owner's phone (target < 5 s).
6. Owner opens the dashboard, sees the conversation, replies personally.
7. Gate decision logged to BigQuery.

### Walkthrough C: Ambiguous / low-confidence → dashboard queue → owner reviews

1. Customer sends "Do you do the thing from last time?" on WhatsApp.
2. Ingested and classified: intent = FAQ, sentiment = neutral.
3. RAG best match confidence = 0.41.
4. Gate fails on condition 2 → message placed in the dashboard queue.
5. Owner reviews at their convenience and replies from the dashboard.
6. Gate decision logged to BigQuery (useful for tuning the threshold and finding FAQ gaps).

## GCP Services Diagram

```
 WhatsApp        Instagram         Gmail
    │                │               │
    └───────┬────────┴───────┬───────┘
            ▼                ▼
   ┌──────────────────────────────┐
   │ Cloud Run (webhook receivers)│── validate ──► Firestore (messages)
   └──────────────┬───────────────┘
                  ▼
   ┌──────────────────────────────┐
   │ Pub/Sub (1 topic per channel)│
   └──────────────┬───────────────┘
                  ▼
   ┌──────────────────────────────┐
   │ Cloud Run (classify pipeline)│
   │  • Natural Language API      │ intent + sentiment
   │  • Gemini embeddings         │
   │  • Firestore vector search   │ FAQ match + confidence
   └──────────────┬───────────────┘
                  ▼
        ┌───────────────────┐        every decision
        │  CONFIDENCE GATE  │──────────────────────────► BigQuery ─► Looker Studio
        └───┬───────┬───────┘
   all pass │       │ negative / urgent          low confidence / complex
            ▼       ▼                                   ▼
   ┌────────────┐ ┌──────────────┐          ┌──────────────────────┐
   │ Vertex AI  │ │ FCM push     │          │ Dashboard queue      │
   │ (Gemini)   │ │ to owner     │          │ (Firestore)          │
   └─────┬──────┘ └──────┬───────┘          └──────────┬───────────┘
         ▼               └──────────────┬──────────────┘
   ┌────────────┐                       ▼
   │ Cloud Func │            ┌─────────────────────┐
   │ (gated     │            │ Owner dashboard     │
   │  send)     │◄───────────│ React/Next.js       │
   └─────┬──────┘ owner reply│ (Firebase Hosting)  │
         ▼                   └─────────────────────┘
  WhatsApp Cloud API / Instagram Graph API / Gmail API
```

## Key Design Decisions

- **Cloud Run for webhooks** — scalable, serverless, per-request billing. Fits bursty, unpredictable webhook traffic from small businesses.
- **Pub/Sub, one topic per channel** — decouples ingestion from processing so webhooks can return fast; per-channel topics keep routing, retries, and failure isolation separate.
- **Firestore** — real-time listeners power the live dashboard; schemaless fits varied channel payloads; documents map naturally onto conversation threads.
- **Tunable confidence gate** — threshold lives in configuration, not code. Starts at 0.85 and is tuned from BigQuery gate-decision data.
- **Gemini only after the gate passes** — messages routed to push or the dashboard never incur an LLM call, which controls cost and avoids generating replies that will never be sent.
