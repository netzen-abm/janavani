# Janavani — Shared Infrastructure First Rule

## Status
Canonical engineering invariant.

## Rule
Every new Janavani skill, capability, feature, workflow primitive, intelligence function, provider integration, security control, data service, or infrastructure component MUST be designed as reusable shared infrastructure first.

A feature MUST NOT be implemented directly inside WebApp, Telegram Bot, Telegram Mini App, Android, iOS, WhatsApp, Messenger, DApp, or any other access surface when the underlying behavior can be shared.

## Required dependency direction

```text
Access Surface
      ↓
Shared Application Contract
      ↓
Shared Capability
      ↓
Shared Infrastructure / Provider Adapter
      ↓
Provider implementation
```

Never:

```text
WebApp → private feature implementation
Telegram → duplicate feature implementation
Mobile → duplicate feature implementation
```

## Applicability
This rule applies equally to:

- civic workflows;
- Case management;
- Evidence and provenance;
- Authority discovery;
- Document generation and quality checks;
- Legal/public-source intelligence;
- AI, RAG, OCR, translation and VLM functions;
- Agentic AI and tool execution;
- Identity, consent and permissions;
- Privacy and safety controls;
- Storage and synchronization;
- Search and indexing;
- Notifications;
- Submission and tracking;
- Analytics and feedback;
- localization and language services;
- decentralized protocols and transports;
- Freenet, Nostr, P2P, mesh, blockchain and future providers;
- any new skill or product feature discovered during development.

## New-feature gate
Before implementation, answer:

1. What reusable capability does this belong to?
2. What stable input/output contract does it expose?
3. Which access surfaces can consume it?
4. Which provider implementations can satisfy it?
5. What privacy/safety policy governs it?
6. How does it behave when the provider is unavailable?
7. What tests prove the contract independently of a UI?
8. What documentation makes the capability reusable?

If the behavior is currently implemented only in one access surface, it is not considered architecturally complete until the reusable boundary is defined or the reason for non-sharing is explicitly documented.

## User choice
Platform completeness and user choice are separate concerns.

A capability may be available across the ecosystem while the user chooses whether to invoke it. AI is the canonical example: AI capability is platform infrastructure; AI assistance remains optional to the user.

## Definition of done
A new feature is not "done" because its screen, bot command, or endpoint works. It is done only when:

- the shared capability contract exists;
- the capability is independently testable;
- access surfaces consume the shared contract;
- provider-specific logic is isolated behind adapters;
- privacy/safety controls are enforced at the shared boundary;
- failure/degraded behavior is defined;
- provenance/audit requirements are satisfied where applicable;
- documentation and versioning are present.

## Architectural objective
Janavani should accumulate a **capability fabric**, not a collection of channel-specific applications.

Every engineering increment should increase the reusable infrastructure available to all compatible Janavani surfaces.
