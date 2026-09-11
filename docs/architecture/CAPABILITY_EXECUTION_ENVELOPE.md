# Janavani — Canonical Capability Execution Envelope

**Status:** PROPOSED IMPLEMENTATION CONTRACT

## Purpose

Every shared Janavani capability invocation must carry one provider-neutral execution context. Interfaces and providers may add transport-specific metadata, but they must not create competing domain execution semantics.

## Required context

- operation identity
- correlation identity
- optional parent operation
- authenticated identity context
- capability ID and action
- resource ID when applicable
- originating surface
- idempotency key for external side effects
- authorization reference/decision context
- consent references where required
- policy/risk context
- side-effect classification
- provenance records

## Trust classes

Citizen-provided, authoritative, system-derived, expert-reviewed, AI-generated and unverified information remain distinguishable.

## Invariants

1. External side effects require idempotency.
2. Provider failure must not be represented as capability success.
3. AI output never becomes authoritative solely because a model produced it.
4. Consequential operations remain subject to authorization, consent and explicit approval where policy requires it.
5. Execution context is shared infrastructure and must not depend on Web, Telegram, mobile, database, AI or decentralized providers.
6. The same operation can be traced across multiple adapters without creating a second domain implementation.
