# Janavani Ecosystem Shared Infrastructure Contract

## Purpose

Janavani is the first civic vertical on a provider-neutral, privacy-first shared infrastructure. Shared infrastructure is extracted only where it creates an independent boundary of trust, persistence, provider dependency, change, or reuse.

## Core layers

1. **Capability contracts** — surface-neutral business capabilities.
2. **Execution/security envelope** — authenticated identity, authorization, purpose, consent and capability-scoped execution context.
3. **Privacy boundary** — device-first personal/sensitive content handling; no durable citizen-content repository.
4. **Persistence ports** — provider-neutral repositories; providers remain replaceable.
5. **Provider adapters** — PostgreSQL, object storage, local/test implementations and future providers.
6. **Surface adapters** — WebApp, Telegram and future independent surfaces.
7. **Document boundary** — compose/review/generate/download only.
8. **Authority intelligence** — verified public institutional information, provenance and jurisdiction resolution.
9. **Observability/security** — metadata-only telemetry; never raw citizen content.

## Independence rule

Each surface must be able to fail independently. Telegram failure must not break WebApp operation; WebApp failure must not break Telegram operation. Shared contracts may be common; surface orchestration must not be.

## Privacy rule

Personal and sensitive citizen information remains on the citizen device whenever technically possible. If transport processing is unavoidable, it is transient, purpose-bound and never durable Janavani storage.

## Document rule

Janavani never sends documents. Complaint, petition, RTI and related artifacts terminate at citizen review and download. The citizen performs all external sending.

## Decomposition rule

Do not split modules because of file size alone. Split only when the split creates an independent architectural boundary. Keep tightly coupled invariants and orchestration together when splitting would duplicate state transitions or weaken correctness.

## Provider neutrality

Business capabilities depend on interfaces/contracts, never on PostgreSQL/S3/Telegram/FastAPI-specific implementations.

## Future ecosystem reuse

A future health, wellness, research or other ecosystem product may reuse the capability/security/privacy/provider layers without inheriting Janavani-specific civic domain logic.

