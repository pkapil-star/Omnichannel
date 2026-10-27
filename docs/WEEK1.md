# Week 1 Work

Foundation week, branch `backend` (2026-10-21 to 2026-10-28).

## Timeline

| Date | Work | Commit |
|---|---|---|
| 10-21 | Project scaffold docs (PRD, ARCHITECTURE) and CLAUDE.md rules | 4f524b5 |
| 10-21 | Cosmos/Firestore schema proposal, Gemini via AI Studio | 2ab811e |
| 10-21 | Labeled dataset (125 rows), sample FAQs (12), dataset test | 39f8bf9 |
| 10-21 | Message simulator `backend/simulator.py` | af93cf4 |
| 10-22 | Gemini zero-shot intent/sentiment classifier and `evaluate.py` | c8e5d6a |
| 10-22 | Branch workflow rules (`main`, `frontend`, `backend`) | 985b7e2 |
| 10-27 | Trained intent and sentiment classifiers on Gemini embeddings | 5509675 |
| 10-28 | Switched Gemini client back to AI Studio key (no billing) | 1059a16 |
| 10-28 | Cloud moved from GCP to Azure for Students, docs updated | 242be79 |
| 10-28 | Model training rule and Azure plan added to CLAUDE.md | 25a51f7 |

## Deliverables

- **Docs** (`docs/`): PRD, ARCHITECTURE, SCHEMA (proposed), MEMORY.
- **Data** (`data-pipeline/`): `dataset.jsonl` (125 rows: intent, sentiment, FAQ match, expected route), `faqs.json` (12 FAQs, demo salon).
- **Simulator** (`backend/simulator.py`): sends test messages, dry run with `-` as URL.
- **Zero-shot baseline** (`backend/classifier.py`, `data-pipeline/evaluate.py`): `classify()` for intent and sentiment, `embed()` for embeddings.
- **Trained models** (`data-pipeline/train.py`): `gemini-embedding-001` embeddings plus scikit-learn Logistic Regression (`class_weight="balanced"`), scored with 5-fold stratified CV. Saved to `data-pipeline/models/` with `metrics.json`.

## ML results (5-fold CV, 125 rows)

| Task | Accuracy | Macro-F1 | Weakest class |
|---|---|---|---|
| Intent | 92.0% | 0.88 | `other` 0.74 (14 examples) |
| Sentiment | 92.8% | 0.85 | `positive` 0.61 (12 examples) |

The Gemini zero-shot baseline for comparison is not run yet (free tier is about 20 requests/day).

## Decisions

- Cloud moved from GCP to Azure for Students (no GCP billing): Container Apps, Service Bus, Azure Functions, Cosmos DB (data, vector search, `gate_logs`), Static Web Apps.
- Firebase kept only for Auth and FCM push.
- Model training is in scope, offline evaluation first. A trained model enters the gate only with developer approval.
- Auto-reply is RAG-only: confident FAQ match and non-negative sentiment. Complaints only notify the owner.
- Dashboard polls the Functions API every 3-5 s.

## Not done yet

- Azure for Students activation, budget alert, resource group (developer action).
- Cosmos DB schema approval (`docs/SCHEMA.md`).
- Gemini zero-shot baseline run and the gate-confidence calibrator.
- Trained models are not wired into the live pipeline.
