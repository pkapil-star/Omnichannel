<!-- Omnichannel AI Support Agent for Local Businesses — Living project state tracker (read and update as work progresses) -->

# Project Memory

## Current Phase

Phase 1 — Ingest + Classify + Notify (in progress)

## What's Built

- Docs: PRD, ARCHITECTURE, SCHEMA, MEMORY in `docs/`
- Labeled dataset (125 rows) and sample FAQ file (12 FAQs) in `data-pipeline/`
- Simulator script `backend/simulator.py`
- Repo with 3 branches on GitHub

## What's In Progress

_(Empty)_

## Decisions Made

- Confidence threshold: starting at 0.85 (to be tuned via BigQuery data)
- Initial channels: WhatsApp + Gmail (Instagram added in Phase 2)
- Dashboard: React/Next.js (not Vue, not plain HTML)
- Dashboard hosting: Firebase Hosting (decided for simplicity)
- No model training — API-only approach confirmed
- Firestore native vector search replaces Vertex AI Vector Search (free-tier friendly)
- Gemini on Vertex AI via `google-genai` SDK, ADC auth, project in `GCP_PROJECT_ID`. Replaced the AI Studio key because the free tier allows only 20 requests/day per model, too low for the 125-row evaluation and the demo
- Multi-tenant Firestore schema approved, see `docs/SCHEMA.md`
- Branches: `main`, `frontend`, `backend`. Functions and data-pipeline live on `backend`
- Initial channels for the 4-week demo: WhatsApp (Meta test number) + simulator script. Gmail and Instagram are future work

## Open Questions

- How to handle Firestore conversation truncation for long threads passed to Gemini?
- Cold-start mitigation for Cloud Run — use min-instances=1 or accept latency?
- Rate limit handling for WhatsApp Cloud API (429 → exponential backoff strategy?)

## Blockers

None currently.

## Next Steps

1. Developer: create GCP project, budget alert, enable APIs (needs card for trial)
2. Developer: install gcloud, run `gcloud auth application-default login`, set `GCP_PROJECT_ID` in local `.env` (never commit)
3. Create Cloud Run webhook receiver for WhatsApp
4. Configure Pub/Sub topic for WhatsApp channel
5. Create Firestore collections, indexes and seed the demo business and FAQs
