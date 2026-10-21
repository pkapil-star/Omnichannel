<!-- Omnichannel AI Support Agent for Local Businesses — Rules for Claude Code -->

# CLAUDE.md

## Project Context

- Unifies WhatsApp, Instagram, and Gmail messages for small local businesses into one owner dashboard on GCP.
- Classifies intent and sentiment, scores FAQ-match confidence (Vertex AI Vector Search), and routes via a 3-branch gate: auto-reply (Gemini), FCM push, or dashboard queue.
- API-only ML (Vertex AI / Gemini / Natural Language API). No model training. See `docs/PRD.md`, `docs/ARCHITECTURE.md`, `docs/MEMORY.md`.

## Rules

1. **Never change the auto-reply gate without explicit test** — Before any change to the confidence threshold or gate logic, ask the developer. This is the most sensitive part of the system.

2. **Firestore schema changes need discussion first** — Don't add or rename fields in conversation documents without checking. Migrations are manual here.

3. **Env vars only via .env files** — Never hardcode API keys, project IDs, or secrets. Always use `process.env` / dotenv. Remind the developer if you see a hardcoded secret.

4. **Channel send APIs are gated** — The outbound Cloud Function must check the confidence gate result before calling any channel send API. Never add a direct send API call outside the gated Cloud Function.

5. **One topic per channel in Pub/Sub** — Do not combine channels into a single topic. Routing is intentionally separate per channel.

6. **Commit style** — Use Conventional Commits: `feat:`, `fix:`, `refactor:`, `chore:`, `docs:`. Keep commits small and focused.

7. **No model training** — This project uses Vertex AI and Gemini APIs only. Do not add training loops, fine-tuning scripts, or dataset pipelines.

8. **Test before PR** — Always run available tests and lint before pushing. If no test exists for a new feature, write at least one unit test for the critical path.

9. **Dashboard and backend are separate** — Keep the React/Next.js dashboard and Cloud Run backend as separate services. Do not mix frontend code into backend folders.

10. **Log everything to BigQuery** — Every gate decision (pass/fail, confidence score, intent, channel) must be logged. Never skip BigQuery logging for a gate evaluation.

11. **Use the ponytail skill for all code** — Invoke the `ponytail` skill before writing, changing, or reviewing any code. Simplest working solution first.

12. **Update MEMORY.md only after major changes** — Major = new service/module, architecture or stack decision, schema change, gate change, phase completed. Skip for small edits, typos, minor fixes.

13. **Dual-subject project: Cloud + ML** — This project is graded in two subjects. Both must work end to end.
    - Cloud: Cloud Run, Cloud Functions, Pub/Sub, Firestore, BigQuery, FCM, IAM, deploy config.
    - ML (API-only): intent/sentiment classification, embeddings + Vector Search FAQ matching, confidence scoring, Gemini reply generation, evaluation of the gate (accuracy/precision on a labeled test set).
    - Do not ship a feature that only satisfies one side. Flag gaps to the developer.

14. **Branch workflow** — Three branches: `main`, `frontend`, `backend`. Dashboard work goes on `frontend`, backend/functions/data-pipeline work on `backend`. Merge to `main` via PR only after tests and lint pass. Never commit directly to `main`.

## Folder Structure (expected)

```
/backend        → Cloud Run webhook receivers, Pub/Sub handlers, classification pipeline
/functions      → Cloud Functions (gated outbound send)
/dashboard      → React/Next.js owner dashboard
/data-pipeline  → Vertex AI indexing scripts, FAQ seeding
/docs           → PRD, ARCHITECTURE, MEMORY
/infra          → Terraform / gcloud config scripts (optional)
```
