<!-- Omnichannel AI Support Agent for Local Businesses — Rules for Claude Code -->

# CLAUDE.md

## Project Context

- Unifies WhatsApp, Instagram, and Gmail messages for small local businesses into one owner dashboard on GCP.
- Classifies intent and sentiment, scores FAQ-match confidence (Firestore vector search), and routes via a 3-branch gate: auto-reply (Gemini), FCM push, or dashboard queue.
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
    - Two folders, one repo (git worktree): `Omnichannel ( ml and cloud )` is always `backend`, sibling `Omnichannel-frontend` is always `frontend`. Never run `git checkout` to change a folder's branch. Frontend/dashboard work happens only in `Omnichannel-frontend`; never write dashboard files in the backend folder.

15. **No Claude attribution** — Never add `Co-Authored-By: Claude` or "Generated with Claude Code" lines to commits or PRs.

## Folder Structure (expected)

```
/backend        → Cloud Run webhook receivers, Pub/Sub handlers, classification pipeline
/functions      → Cloud Functions (gated outbound send)
/dashboard      → React/Next.js owner dashboard
/data-pipeline  → Vertex AI indexing scripts, FAQ seeding
/docs           → PRD, ARCHITECTURE, MEMORY
/infra          → Terraform / gcloud config scripts (optional)
```

## 4-Week Plan (demo for professors)

Goal: deployed, demoable system plus visible planning and ML evidence. Free tier only (GCP trial credit, AI Studio key). Channels: WhatsApp (Meta test number) + simulator script. Instagram and Gmail are future work unless time remains.

Proposed (pending developer OK): Firestore native vector search instead of Vertex Vector Search; Gemini via AI Studio API key (kept behind one function for a later Vertex switch).

| Week | Goal | Cloud | ML | Branch |
|---|---|---|---|---|
| 1 | Foundation | GCP project, budget alert, enable APIs, Firestore schema (discuss first), simulator script | Labeled dataset (~150 messages), sample FAQ file | `backend` |
| 2 | Phase 1 pipeline | Cloud Run webhook → Pub/Sub → classifier worker → Firestore, FCM push, BigQuery gate log | Intent/sentiment classifier, evaluate on dataset | `backend` |
| 3 | Dashboard + Phase 2 | Dashboard on Firebase Hosting, reply-from-dashboard | Embeddings, vector search, confidence score, Gemini reply, gated send function | `frontend` + `backend` |
| 4 | Prove it | Real WhatsApp hookup, Looker Studio chart, deploy check | Gate evaluation: threshold sweep, false auto-reply rate, results table | both |

Week 4 also: slides, screen-recorded backup demo, short report.

Demo script (5 min): FAQ message auto-replies; angry complaint triggers push, no auto-reply; vague message lands in dashboard queue; show BigQuery gate log and evaluation table.

Priority if time runs short: (1) Phase 1 deployed end to end, (2) evaluation results, (3) RAG + gated auto-reply, (4) dashboard polish, (5) Gmail, then Instagram.

Week 1 checklist:
- [x] Labeled dataset in `data-pipeline/dataset.jsonl` (125 rows: intent, sentiment, FAQ match, expected route)
- [x] Sample FAQ file `data-pipeline/faqs.json` (12 FAQs, demo salon)
- [x] Simulator script `backend/simulator.py` (dry run with `-` as URL)
- [ ] Firestore schema agreed with developer
- [ ] GCP project + budget alert + APIs enabled (developer action: needs card for trial)

## Frontend Plan (`dashboard/`, branch `frontend`)

Stack: Next.js (static export, `output: 'export'`) + Tailwind, Firebase web SDK (Firestore `onSnapshot`, Auth, FCM) on Firebase Hosting. No SSR, no Cloud Run for the dashboard, so it stays free. Single owner login (Google sign-in, one allowed email). Firebase config only via `.env.local` (rule 3). Dashboard never calls a channel send API; owner replies go to the gated Cloud Function (rule 4).

Screens (keep to three):
1. **Inbox**: live message queue, filter by route (queue / push / auto-replied) and channel, unread badge.
2. **Conversation**: thread, chips for intent, sentiment, confidence and gate route, reply box.
3. **Analytics**: KPI cards (volume, auto-reply rate, per-channel split) plus embedded Looker Studio chart.

| Week | Frontend goal | Depends on backend |
|---|---|---|
| 1 | Scaffold `dashboard/`, Tailwind, `.env.local.example`. Inbox + Conversation screens on mock data built from `data-pipeline/dataset.jsonl` | Nothing (mock data) |
| 2 | Swap mock for Firestore `onSnapshot` (emulator or real project). Google sign-in + owner-only rules. FCM web push: service worker, save device token | Firestore schema agreed; messages carry intent, sentiment, confidence, route |
| 3 | Reply box wired to the gated Cloud Function. Gate badges and "auto-replied by AI" marker in threads. Deploy to Firebase Hosting. KPI cards | Reply endpoint; FCM tokens collection |
| 4 | Looker Studio embed, mobile-responsive pass, seeded demo data, screenshots for the report | BigQuery gate log |

Rules for this track:
- Frontend can start in Week 1 with no backend, using mock data. Mock shape must match the agreed Firestore schema, so agree the schema first.
- Reply path needs a decision before Week 3: dashboard calls the Cloud Function over HTTPS (with Firebase ID token), not Firestore-triggered send.
- Skip for demo: multi-user, settings pages, dark mode, i18n, SSR.
- Run `lint` and `build` before every PR to `main` (rule 8).
