# Accountability Feedback Provider Boundary

## Decision

Accountability Feedback is a canonical persisted domain and therefore participates in the shared `ProviderComposition` boundary.

The access surfaces must not instantiate `JsonlAccountabilityFeedbackRepository` or another concrete persistence adapter directly. They request the repository through shared platform composition.

## Current providers

- `memory` — default for development and tests.
- `jsonl` — bounded durable/local adapter retaining the existing `database/ratings.jsonl` representation.

No PostgreSQL adapter is introduced by this change. PostgreSQL should be added only when durable PostgreSQL persistence is actually required and the schema, transaction, privacy, authorization, and migration evidence is available.

## Safety

- The legacy `database/ratings.jsonl` source remains preserved.
- No migration or destructive transformation is performed.
- Provider composition does not instantiate database clients.
- Decision-only Follow-Up and Escalation remain outside persistence composition.
- Telegram remains an access surface and does not own persistence selection.
