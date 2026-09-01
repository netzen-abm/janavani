# Janavani Architecture Authority

**Status:** Authoritative convergence document  
**Date:** 2026-08-26

## Purpose

This document identifies the authoritative implementation boundary for each cross-ecosystem concern. It exists to prevent multiple generations of code, duplicate runtime entry points, competing contracts, and accidental reintroduction of client-specific business logic.

## Non-negotiable principles

1. **Archive first; delete only after evidence.**
2. **Green means verified behavior.** Tests, mocks, configuration, or provider diagnostics must not be represented as stronger evidence than they actually provide.
3. **Optional means user choice.** The ecosystem retains the capability even when a user does not use it.
4. **Access surfaces are independently operable.** Android, iOS, Web, DApp, Telegram, Telegram Mini App, WhatsApp, Messenger, CLI and future adapters must not require another access surface at runtime.
5. **Shared capability is preferred over duplicated business logic.** Clients consume stable contracts and adapters; clients do not become competing domain authorities.
6. **Privacy and safety are by design and by default.**

## Authority matrix

| Concern | Current authority | Rule for alternatives |
|---|---|---|
| Canonical HTTP API | `src.web.canonical_app:app` | Historical app entry points are compatibility/legacy only until audited. |
| Container API startup | `src.web.canonical_app:app` | Do not introduce another production Docker application target. |
| Civic case lifecycle | shared civic-case domain contract | Client surfaces consume the contract; they do not own lifecycle semantics. |
| Storage abstraction | `StorageAdapter` boundary | Provider-specific repositories remain behind the boundary. |
| Privacy boundary | central privacy capability | Do not duplicate sensitive-field policy in individual clients. |
| App/DApp capability semantics | shared client capability contract | Android/iOS/DApp adapters remain independent. |
| AI/Agentic AI | capability/provider abstraction | No AI provider is a mandatory runtime dependency of unrelated capabilities. |
| Messaging | channel adapters | Telegram, WhatsApp and Messenger remain independently deployable. |
| Delivery state | explicit delivery semantics | `SENT` must never be represented as confirmed delivery. |
| Authority resolution | explicit authority contract | Ambiguous or unverified authority must not be silently selected. |
| Evidence | evidence contract | Integrity metadata is not proof that evidence is truthful. |
| Documents | shared document contract | Export/submission requires the appropriate user approval. |

## Evidence levels

Every capability should be classified as one of:

- **VERIFIED** — executable evidence demonstrates the behavior claimed.
- **PARTIALLY VERIFIED** — meaningful executable evidence exists but material paths remain unverified.
- **CONFIGURED** — configuration exists, but execution evidence is incomplete.
- **UNVERIFIED** — the repository claims or describes the capability without sufficient executable evidence.
- **FAILED** — an applicable verification currently fails.
- **BLOCKED** — verification cannot proceed because a prerequisite is broken.

A mock or fake provider may verify an adapter boundary when that is the stated test purpose. It must not be presented as proof that the real provider works.

## Runtime convergence rule

Before adding or modifying a runtime entry point, determine whether it is:

1. canonical;
2. compatibility-only;
3. legacy awaiting archival;
4. experimental; or
5. invalid/duplicate.

New production code must not silently create a second authority.

## Change-control rule

When a new capability is implemented:

1. add or update the executable contract;
2. add appropriate verification;
3. classify its evidence level;
4. document the capability and its independent failure behavior;
5. update the relevant architecture/roadmap authority document in the same change set.

When a capability is removed or superseded, archive the previous implementation/documentation first and retain the evidence needed to justify later deletion.

## Independence rule

A shared infrastructure dependency is acceptable when it provides a stable capability contract. A runtime dependency between user-facing access surfaces is not.

For example:

`Telegram failure != Android failure`  
`DApp failure != Web failure`  
`AI provider failure != civic case failure`  
`WhatsApp failure != Messenger failure`

Degraded behavior must be explicit and truthful.
