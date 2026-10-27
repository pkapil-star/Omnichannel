<!-- Omnichannel AI Support Agent for Local Businesses — Living project state tracker (read and update as work progresses) -->

# Project Memory

## Current Phase

Phase 1 — Ingest + Classify + Notify (in progress)

## What's Built

- Docs: PRD, ARCHITECTURE, SCHEMA, MEMORY in `docs/`
- Labeled dataset (125 rows) and sample FAQ file (12 FAQs) in `data-pipeline/`
- Simulator script `backend/simulator.py`
- Repo with 3 branches on GitHub
- Gemini zero-shot classifier `backend/classifier.py` (`classify()` for intent + sentiment, `embed()` for embeddings) and `data-pipeline/evaluate.py` (scores it on the dataset, a full run writes `baseline.json`)
- **Trained models (2026-10-27, commit 5509675)**: `data-pipeline/train.py` embeds the 125 rows with `gemini-embedding-001` (cached in `embeddings.npz`, gitignored), trains scikit-learn Logistic Regression (`class_weight="balanced"`), and scores it with 5-fold stratified CV. Saves `data-pipeline/models/{intent,sent}.joblib` and `metrics.json`. Unit test `test_train.py` needs no API
  - Intent: 92.0% accuracy, macro-F1 0.88 (weakest: `other` 0.74, 14 examples)
  - Sentiment: 92.8% accuracy, macro-F1 0.85 (negative 1.00, weakest: `positive` 0.61, 12 examples)
  - Free tier embeds 100 texts/minute, so `train.py` waits 61 s between batches of 50
- Local Python venv `.venv/` (gitignored), deps in `backend/requirements.txt` (`google-genai`, `scikit-learn`)

## What's In Progress

- Gemini zero-shot baseline for the trained-vs-API comparison: run `evaluate.py` in full (125 calls, limited by the ~20/day free tier), then re-run `train.py` so `metrics.json` includes it
- Gate-confidence calibrator (second trained model): not started. Offline only until the developer approves it for the gate (rule 1)
- Trained models are not wired into the live pipeline. The backend still classifies with the Gemini prompt

## Decisions Made

- Confidence threshold: starting at 0.85 (to be tuned via `gate_logs` data)
- Initial channels: WhatsApp + Gmail (Instagram added in Phase 2)
- Dashboard: React/Next.js (not Vue, not plain HTML)
- Model training IS in scope (reversed the earlier API-only decision; the developer must show training to present the project). Plan: scikit-learn models trained locally in `data-pipeline/` on Gemini embeddings, (1) intent/sentiment classifier, (2) gate-confidence calibrator, both compared to the Gemini zero-shot baseline on a held-out split. Offline evaluation first; entering the live gate needs developer approval
- **Cloud moved from GCP to Azure for Students (2026-10-27)**: no GCP billing available. The project PDF will be updated to match. Mapping: Container Apps (webhooks, classifier worker), Service Bus Standard (topic per channel), Azure Functions (gated send + dashboard API), Cosmos DB free tier (data + vector search + `gate_logs`), Static Web Apps (dashboard hosting)
- Firebase kept only for Auth (Google sign-in) and FCM web push, on the free Spark plan. Firestore and BigQuery are no longer used
- Dashboard polls the Functions API every 3-5 s instead of realtime listeners. SignalR is the upgrade path
- Gate log is the Cosmos DB `gate_logs` container (replaces BigQuery); analytics charts come from it, no Looker Studio
- Gemini via AI Studio key (`GEMINI_API_KEY`) through `google-genai`, behind one function. Back to the key from Vertex because there is no billing. Free tier is about 20 requests/day per model, enough for the demo but not for running all 125 rows at once; spread the evaluation over days or use a model with a higher limit
- Cosmos DB schema is proposed in `docs/SCHEMA.md` (same fields as the approved Firestore schema plus `id`, `businessId`, `conversationId`). Needs developer approval before use
- Branches: `main`, `frontend`, `backend`. Functions and data-pipeline live on `backend`
- Initial channels for the 4-week demo: WhatsApp (Meta test number) + simulator script. Gmail and Instagram are future work

- Auto-reply stays on, RAG-only: confident FAQ + non-negative sentiment gets a reply; complaints and negative sentiment only notify the owner. This extends the project PDF, which says the agent never sends replies. State this in the report and demo
- Plan: 4 weeks, dashboard has Inbox and Conversation screens plus Analytics from `gate_logs` (Looker Studio dropped with BigQuery). Frontend prompt written, mock data from `data-pipeline/dataset.jsonl`
- Pending developer OK ("apply"): web chat widget as the real channel instead of WhatsApp (avoids Meta approval delay), Gemini one-line owner summary on every message, one Gemini call for intent + sentiment + summary. Not yet in PRD/ARCHITECTURE

## Open Questions

- Should the trained intent/sentiment models replace the Gemini prompt in the live classifier (cheaper, no daily limit), or stay offline evidence only? Gate change, needs developer approval
- Working-tree files were converted to CRLF by another tool, while the repo uses LF. Add a `.gitattributes` (`* text=auto eol=lf`) to stop the noise?

- How to handle conversation truncation for long threads passed to Gemini?
- Cold-start mitigation for Container Apps — use min replicas=1 or accept latency?
- Rate limit handling for WhatsApp Cloud API (429 → exponential backoff strategy?)
- Service Bus topics need the Standard tier (about $10/month). Confirm it fits the student credit, otherwise fall back to queues named per channel

## Blockers

- Azure for Students not activated yet (developer action: sign up with college email)

## Next Steps

1. Developer: activate Azure for Students, create a resource group and a budget alert (Gemini key is already in `.env`)
2. Developer: approve or change the Cosmos DB schema in `docs/SCHEMA.md`
3. Developer: reply "apply" to add the web widget, summary and one-call classification to PRD, ARCHITECTURE and CLAUDE.md
4. Commit the Azure doc switch, the AI Studio key switch in `classifier.py`, and the training rule in CLAUDE.md on `backend` (training code is already committed)
5. ML: run the Gemini baseline, then build the gate-confidence calibrator with a threshold sweep and false auto-reply rate
6. Add ~15-20 labeled `other` and `positive` rows to lift the weakest classes
7. Backend: gate function, tested against `data-pipeline/dataset.jsonl`
8. Backend: Container Apps webhook receiver, Service Bus topic per channel, Cosmos DB containers per `docs/SCHEMA.md`, seed demo business and FAQs
9. Frontend (branch `frontend`): scaffold `dashboard/`, Inbox and Conversation screens on mock data
