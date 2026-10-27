<!-- Omnichannel AI Support Agent for Local Businesses — Cosmos DB schema (PROPOSED for Azure, pending developer approval) -->

# Schema

Multi-tenant from the start. Every conversation belongs to a business. Only one demo business is seeded.

Changing any field below needs developer approval (CLAUDE.md rule 2).

**Status: proposed.** The earlier Firestore schema was approved. This is the same data moved to Cosmos DB for NoSQL. Every field name is unchanged. The only additions are the ones Cosmos needs: `id` on every document, and `businessId` / `conversationId` because Cosmos has no subcollections.

## Cosmos DB

Database `omnichannel`, five containers (free tier: 1000 RU/s shared, 25 GB).

```
businesses            partition key /id
  id (= bid), name, ownerUid, createdAt
  channels: { whatsapp: { phoneNumberId } }
  fcmTokens: [string]

faqs                  partition key /businessId
  id, businessId, question, answer, updatedAt
  embedding: vector(768)

conversations         partition key /businessId
  id, businessId
  channel: "whatsapp" | "simulator"
  customerId, customerName
  status: "open" | "resolved"
  route: "auto_reply" | "push" | "queue"    latest gate result
  lastMessageAt, lastMessagePreview, unread

messages              partition key /conversationId
  id, conversationId, businessId
  direction: "in" | "out"
  text, ts, channelMessageId
  intent, sentiment, faqMatchId, confidence    inbound only
  sentBy: "auto" | "owner"                     outbound only

gate_logs             partition key /businessId
  id, businessId, conversationId, messageId, channel
  intent, sentiment, confidence, route, ts
```

### Notes

- `embedding` stays 768 dimensions: the Gemini embedding model defaults to 3072, so the request sets `output_dimensionality=768`. Cosmos allows more, but 768 keeps RU cost and storage low.
- The confidence threshold is not stored in the database. It lives in config or env, so changing it stays a deliberate gate change (CLAUDE.md rule 1).
- New channels (Gmail, Instagram) add values to the `channel` enum. No field is renamed.
- `gate_logs` replaces the BigQuery table. One row per gate evaluation, pass or fail (CLAUDE.md rule 10). The columns are the same as before.

### Indexes

- Vector index on `/embedding` in `faqs`, cosine distance, 768 dimensions, type `quantizedFlat` (12 FAQs, no need for DiskANN). The container's vector embedding policy must be set at creation; it cannot be added later.
- Composite index on `conversations`: `/status` ascending, `/lastMessageAt` descending.
- Exclude `/embedding/*` from the default range index.
