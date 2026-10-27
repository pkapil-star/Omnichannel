<!-- Omnichannel AI Support Agent for Local Businesses — Product Requirements Document -->

# Product Requirements Document

## Project Overview

An AI-powered system that unifies incoming messages from WhatsApp, Instagram, and Gmail for small business owners into a single dashboard. The system classifies messages, scores confidence, and uses a hybrid auto-reply design:

- **High-confidence FAQ match + non-negative sentiment** → Gemini generates reply → Azure Function sends via channel API automatically
- **Urgent / negative sentiment** → FCM push notification to owner's phone immediately
- **Low-confidence / complex / booking / complaint** → Dashboard queue, owner replies personally

## Problem Statement

Small business owners miss messages across multiple platforms. There is no single inbox. They reply late or not at all, losing customers.

## Target Users

Local service businesses (salons, parlours, repair shops, restaurants) — typically 1–5 person teams with no dedicated support staff.

## Core Features

1. Webhook receivers for WhatsApp, Instagram, Gmail
2. Intent classification (FAQ / booking / complaint / other) using NLP
3. Sentiment scoring (positive / neutral / negative)
4. RAG-based FAQ matching with confidence scoring via Cosmos DB vector search
5. Conditional auto-reply: only fires when intent = FAQ, confidence ≥ threshold (e.g. 0.85), sentiment ≠ negative
6. Push notification (FCM) for urgent/negative messages
7. Owner dashboard: message queue, conversation history, reply-from-dashboard, analytics
8. Gate-log analytics (Cosmos DB `gate_logs`): message volume, auto-reply rate, top FAQs, channel breakdown

## Out of Scope (MVP)

- No agentic booking / calendar actions
- No customer-facing bot persona
- No multi-user/team accounts
- No custom model training (API-only)

## MVP Build Phases

- **Phase 1:** Ingest + classify + notify only (no auto-reply)
- **Phase 2:** Add RAG + confidence gate + conditional FAQ auto-reply

## Success Metrics

- Owner sees all messages in one place
- Auto-reply rate > 30% for returning FAQ customers (after Phase 2)
- False auto-reply rate < 2% (wrong reply sent)
- Push notification latency < 5 seconds for urgent messages
