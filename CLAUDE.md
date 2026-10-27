<!-- Omnichannel AI Support Agent for Local Businesses — Rules for Claude Code -->

# CLAUDE.md

## Project Context

- Unifies WhatsApp, Instagram, and Gmail messages for small local businesses into one owner dashboard on Azure (Azure for Students). Firebase is used only for owner login (Auth) and web push (FCM).
- Classifies intent and sentiment, scores FAQ-match confidence (Cosmos DB vector search), and routes via a 3-branch gate: auto-reply (Gemini), FCM push, or dashboard queue.
- Gemini via AI Studio key for embeddings, reply generation and the zero-shot baseline, plus small locally trained models (scikit-learn) for intent/sentiment and gate confidence. See `docs/PRD.md`, `docs/ARCHITECTURE.md`, `docs/MEMORY.md`.

## Rules

1. **Never change the auto-reply gate without explicit test** — Before any change to the confidence threshold or gate logic, ask the developer. This is the most sensitive part of the system.

2. **Cosmos DB schema changes need discussion first** — Don't add or rename fields in conversation documents without checking. Migrations are manual here.

3. **Env vars only via .env files** — Never hardcode API keys, project IDs, or secrets. Always use `process.env` / dotenv. Remind the developer if you see a hardcoded secret.

4. **Channel send APIs are gated** — The outbound Azure Function must check the confidence gate result before calling any channel send API. Never add a direct send API call outside the gated Azure Function.

5. **One topic per channel in Service Bus** — Do not combine channels into a single topic. Routing is intentionally separate per channel.

6. **Commit style** — Use Conventional Commits: `feat:`, `fix:`, `refactor:`, `chore:`, `docs:`. Keep commits small and focused.

7. **Model training is in scope, kept small** — Training is a project requirement (needed for the ML subject demo). Train lightweight models locally in `data-pipeline/` (scikit-learn on Gemini embeddings): an intent/sentiment classifier and a gate-confidence calibrator. Always report against the Gemini zero-shot baseline on a held-out split, and save the model with metrics. No GPU or Vertex fine-tuning jobs unless the developer asks. A trained model enters the gate only after explicit developer approval (rule 1); until then it is evaluated offline.

8. **Test before PR** — Always run available tests and lint before pushing. If no test exists for a new feature, write at least one unit test for the critical path.

9. **Dashboard and backend are separate** — Keep the React/Next.js dashboard and Container Apps backend as separate services. Do not mix frontend code into backend folders.

10. **Log everything to `gate_logs`** — Every gate decision (pass/fail, confidence score, intent, channel) must be logged to the Cosmos DB `gate_logs` container. Never skip logging for a gate evaluation.

11. **Use the ponytail skill for all code** — Invoke the `ponytail` skill before writing, changing, or reviewing any code. Simplest working solution first.

12. **Update MEMORY.md only after major changes** — Major = new service/module, architecture or stack decision, schema change, gate change, phase completed. Skip for small edits, typos, minor fixes.

13. **Dual-subject project: Cloud + ML** — This project is graded in two subjects. Both must work end to end.
    - Cloud: Container Apps, Azure Functions, Service Bus, Cosmos DB, Static Web Apps, FCM, IAM/RBAC, deploy config.
    - ML: trained intent/sentiment classifier and confidence calibrator (train/test split, metrics vs Gemini baseline), embeddings + Cosmos DB vector search FAQ matching, Gemini reply generation, evaluation of the gate (accuracy/precision on a labeled test set).
    - Do not ship a feature that only satisfies one side. Flag gaps to the developer.

14. **Branch workflow** — Three branches: `main`, `frontend`, `backend`. Dashboard work goes on `frontend`, backend/functions/data-pipeline work on `backend`. Merge to `main` via PR only after tests and lint pass. Never commit directly to `main`.
    - One folder. `backend` touches only `backend/`, `functions/`, `data-pipeline/`, `docs/`. `frontend` touches only `dashboard/`. Branches never edit the same files, so merges to `main` do not conflict.
    - Before every `git checkout`, commit (`git add -A && git commit -m "wip: ..."`). Never use `git stash` to switch branches.
    - Close or pause other tools (Antigravity etc.) before switching branches. Never run two agents on different branches in the same folder.

15. **No Claude attribution** — Never add `Co-Authored-By: Claude` or "Generated with Claude Code" lines to commits or PRs.

## Folder Structure (expected)

```
/backend        → Container Apps webhook receivers, Service Bus handlers, classification pipeline
/functions      → Azure Functions (gated outbound send, dashboard API)
/dashboard      → React/Next.js owner dashboard
/data-pipeline  → FAQ embedding/indexing scripts, FAQ seeding
/docs           → PRD, ARCHITECTURE, MEMORY
/infra          → Bicep / az CLI scripts (optional)
```

## 4-Week Plan (demo for professors)

Goal: deployed, demoable system plus visible planning and ML evidence. Free tier only (Azure for Students credit, Gemini AI Studio key, Firebase Spark). Channels: WhatsApp (Meta test number) + simulator script. Instagram and Gmail are future work unless time remains.

Decided: Azure replaces GCP (the project PDF will be updated). Cosmos DB vector search for FAQ matching; Gemini via AI Studio API key, kept behind one function so the provider can change later. Dashboard polls an Azure Functions API (no realtime listeners).

| Week | Goal | Cloud | ML | Branch |
|---|---|---|---|---|
| 1 | Foundation | Azure for Students account, budget alert, resource group, Cosmos schema (discuss first), simulator script | Labeled dataset (~150 messages), sample FAQ file | `backend` |
| 2 | Phase 1 pipeline | Container Apps webhook → Service Bus → classifier worker → Cosmos DB, FCM push, `gate_logs` | Intent/sentiment classifier, evaluate on dataset | `backend` |
| 3 | Dashboard + Phase 2 | Dashboard on Static Web Apps, reply-from-dashboard | Embeddings, vector search, confidence score, Gemini reply, gated send function | `frontend` + `backend` |
| 4 | Prove it | Real WhatsApp hookup, Analytics screen from `gate_logs`, deploy check | Gate evaluation: threshold sweep, false auto-reply rate, results table | both |

Week 4 also: slides, screen-recorded backup demo, short report.

Demo script (5 min): FAQ message auto-replies; angry complaint triggers push, no auto-reply; vague message lands in dashboard queue; show `gate_logs` and evaluation table.

Priority if time runs short: (1) Phase 1 deployed end to end, (2) evaluation results, (3) RAG + gated auto-reply, (4) dashboard polish, (5) Gmail, then Instagram.

Week 1 checklist:
- [x] Labeled dataset in `data-pipeline/dataset.jsonl` (125 rows: intent, sentiment, FAQ match, expected route)
- [x] Sample FAQ file `data-pipeline/faqs.json` (12 FAQs, demo salon)
- [x] Simulator script `backend/simulator.py` (dry run with `-` as URL)
- [ ] Cosmos DB schema agreed with developer (proposal in `docs/SCHEMA.md`)
- [ ] Azure for Students activated + budget alert + resource group (developer action: college email, no card)

## Frontend Plan (`dashboard/`, branch `frontend`)

Stack: Next.js (static export, `output: 'export'`) + Tailwind, Firebase web SDK (Auth, FCM only) on Azure Static Web Apps. Data comes from an Azure Functions HTTP API, polled every 3-5 s (no realtime listeners). No SSR, no container for the dashboard, so it stays free. Single owner login (Google sign-in, one allowed email); the API verifies the Firebase ID token. Firebase and API config only via `.env.local` (rule 3). Dashboard never calls a channel send API; owner replies go to the gated Azure Function (rule 4).

Screens (keep to three):
1. **Inbox**: live message queue, filter by route (queue / push / auto-replied) and channel, unread badge.
2. **Conversation**: thread, chips for intent, sentiment, confidence and gate route, reply box.
3. **Analytics**: KPI cards (volume, auto-reply rate, per-channel split) plus gate-decision charts built from `gate_logs`.

| Week | Frontend goal | Depends on backend |
|---|---|---|
| 1 | Scaffold `dashboard/`, Tailwind, `.env.local.example`. Inbox + Conversation screens on mock data built from `data-pipeline/dataset.jsonl` | Nothing (mock data) |
| 2 | Swap mock for polling the Functions API. Google sign-in (Firebase Auth). FCM web push: service worker, save device token | Cosmos schema agreed; messages carry intent, sentiment, confidence, route; read API |
| 3 | Reply box wired to the gated Azure Function. Gate badges and "auto-replied by AI" marker in threads. Deploy to Static Web Apps. KPI cards | Reply endpoint; FCM tokens stored on the business document |
| 4 | Gate-log charts on Analytics screen, mobile-responsive pass, seeded demo data, screenshots for the report | `gate_logs` read API |

Rules for this track:
- Frontend can start in Week 1 with no backend, using mock data. Mock shape must match the agreed Cosmos schema, so agree the schema first.
- Reply path: dashboard calls the Azure Function over HTTPS (with Firebase ID token), not a database-triggered send.
- Skip for demo: multi-user, settings pages, dark mode, i18n, SSR.
- Run `lint` and `build` before every PR to `main` (rule 8).
