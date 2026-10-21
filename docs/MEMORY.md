<!-- Omnichannel AI Support Agent for Local Businesses — Living project state tracker (read and update as work progresses) -->

# Project Memory

## Current Phase

Phase 1 — Ingest + Classify + Notify (in progress)

## What's Built

_(Empty — to be filled as we build)_

## What's In Progress

_(Empty)_

## Decisions Made

- Confidence threshold: starting at 0.85 (to be tuned via BigQuery data)
- Initial channels: WhatsApp + Gmail (Instagram added in Phase 2)
- Dashboard: React/Next.js (not Vue, not plain HTML)
- Dashboard hosting: Firebase Hosting (decided for simplicity)
- No model training — API-only approach confirmed

## Open Questions

- How to handle Firestore conversation truncation for long threads passed to Gemini?
- Cold-start mitigation for Cloud Run — use min-instances=1 or accept latency?
- Rate limit handling for WhatsApp Cloud API (429 → exponential backoff strategy?)

## Blockers

None currently.

## Next Steps

1. Set up GCP project + enable required APIs
2. Create Cloud Run webhook receiver for WhatsApp
3. Configure Pub/Sub topic for WhatsApp channel
4. Set up Firestore schema for conversations
