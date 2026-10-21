<!-- Omnichannel AI Support Agent for Local Businesses — Firestore and BigQuery schema (approved by developer) -->

# Schema

Multi-tenant from the start. Every conversation belongs to a business. Only one demo business is seeded.

Changing any field below needs developer approval (CLAUDE.md rule 2).

## Firestore

```
businesses/{bid}
  name, ownerUid, createdAt
  channels: { whatsapp: { phoneNumberId } }
  fcmTokens: [string]

businesses/{bid}/faqs/{fid}
  question, answer, updatedAt
  embedding: vector(768)

businesses/{bid}/conversations/{cid}
  channel: "whatsapp" | "simulator"
  customerId, customerName
  status: "open" | "resolved"
  route: "auto_reply" | "push" | "queue"    latest gate result
  lastMessageAt, lastMessagePreview, unread

businesses/{bid}/conversations/{cid}/messages/{mid}
  direction: "in" | "out"
  text, ts, channelMessageId
  intent, sentiment, faqMatchId, confidence    inbound only
  sentBy: "auto" | "owner"                     outbound only
```

### Notes

- `embedding` is 768 dimensions. The Gemini embedding model defaults to 3072, but Firestore vector fields allow at most 2048, so the request sets `output_dimensionality=768`.
- The confidence threshold is not stored in Firestore. It lives in config or env, so changing it stays a deliberate gate change (CLAUDE.md rule 1).
- New channels (Gmail, Instagram) add values to the `channel` enum. No field is renamed.

### Indexes

- Vector index on `faqs.embedding`, cosine distance, 768 dimensions.
- Composite index on `conversations`: `status` ascending, `lastMessageAt` descending.

## BigQuery gate log

One row per gate evaluation, pass or fail (CLAUDE.md rule 10).

| Column | Type |
|---|---|
| business_id | STRING |
| conversation_id | STRING |
| message_id | STRING |
| channel | STRING |
| intent | STRING |
| sentiment | STRING |
| confidence | FLOAT |
| route | STRING |
| ts | TIMESTAMP |
