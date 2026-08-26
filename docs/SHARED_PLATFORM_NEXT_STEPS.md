# Shared Platform — Next Verified Construction Sequence

**Status:** ACTIVE ENGINEERING PLAN  
**Date:** 26 August 2026

## Objective

Converge Janavani's existing implementations into reusable, provider-neutral capabilities while keeping every access surface independently operable.

This is an execution plan, not a new architecture generation. Existing canonical documents and the Capability Registry remain authoritative.

## Sequence

1. **Active runtime boundary** — CI validates current runtime code without allowing historical generations to mask current defects.
2. **Capability → repository → test → deployment mapping** — establish verified ownership before consolidation.
3. **Document capability** — converge composition/rendering/delivery behind the existing document contract.
4. **Storage capability** — place Supabase and future storage implementations behind the provider-neutral storage boundary.
5. **Workflow capability** — keep deterministic workflow execution independent from optional AI/agent implementations.
6. **AI access policy** — route local/cloud/RAG/agentic assistance through governed capability contracts with data minimisation and consent.
7. **Authority intelligence** — separate verified government-source data from AI suggestions; never allow AI to invent recipients or addresses.
8. **Submission and delivery state** — distinguish draft, attempted, queued, accepted and confirmed states.
9. **Independent clients** — expose the same capabilities through Web, Telegram Bot, Telegram Mini App, Android, iOS and other adapters without client-to-client runtime dependencies.
10. **Failure-isolation tests** — verify that optional providers, transports, AI systems and clients can fail without disabling unrelated capabilities.

## First product vertical slice

The first complete user journey remains:

`issue → understanding → authority → draft/action → evidence → review → submission → tracking`

The Dynamic Web is the first active product surface, but the underlying capabilities must remain client-neutral so Telegram and later clients can consume them directly.

## Non-negotiable invariants

- Optional means optional for the user, not optional for the ecosystem.
- No interface owns shared business logic.
- No interface depends on another interface for normal operation.
- AI is optional, replaceable infrastructure.
- Agentic actions are permissioned and auditable.
- Verified authority/source data is distinct from AI-generated suggestions.
- Privacy and safety are defaults, not add-ons.
- Legacy material is archived before deletion.
- A task is not complete without implementation, tests, relevant failure checks, documentation and repository evidence.
