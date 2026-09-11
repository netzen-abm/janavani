# JANAVANI — PROJECT MAP

**Status:** ACTIVE — REPOSITORY NAVIGATION AND OWNERSHIP MAP
**Version:** 2.0
**Date:** 11 September 2026

## 1. Purpose

This document explains where production code, interfaces, shared capabilities, storage, tests and documentation belong. It is a navigation/ownership document, not a replacement for `docs/SOURCE_OF_TRUTH.md` or `docs/JANAVANI_MASTER_ARCHITECTURE.md`.

## 2. Repository model

```text
janavani/
├── src/                 # primary application source
├── api/                 # API-related compatibility/integration code
├── tests/               # automated verification
├── docs/                # active documentation
├── planning/            # active detailed contracts/specifications
├── archive/             # historical/superseded material
├── database/            # datasets/seeds/reference data
├── scripts/             # development/operations utilities
├── .github/             # CI and repository automation
├── Dockerfile
├── docker-compose*.yml
├── render.yaml
├── Procfile
├── requirements.txt
├── pyproject.toml
├── Cargo.toml
├── README.md
└── ROADMAP.md
```

## 3. Architectural flow

```text
Interface / Integration
        ↓
API / Application Boundary
        ↓
Shared Capability
        ↓
Workflow + Domain + Services
        ↓
Data / Trust / Provenance
        ↓
Provider / External System
```

Interfaces consume shared capabilities. They do not own shared business logic.

## 4. `src/` ownership

### `src/domain/`

Canonical business concepts and domain rules. Domain code must remain independent of Telegram, Web, WhatsApp and other interfaces.

### `src/workflow/`

Reusable citizen and platform workflows. Workflow definitions/steps must not be tied to one access surface.

### `src/engine/`

Workflow/state orchestration and execution infrastructure. It orchestrates; it must not become a generic business-logic dumping ground.

### `src/services/`

Application/business services and integrations that coordinate reusable capabilities.

### `src/documents/`

Document composition, standards and output. Generation is separate from electronic submission.

### `src/storage/`

Repository contracts, persistence implementations, storage adapters, cache and provider selection.

### `src/adapters/`

Thin translation boundaries for external interfaces, protocols and providers.

### `src/conversation/`

Interaction/session/routing infrastructure. It may orchestrate conversations but must delegate shared business rules.

### `src/web/`

Web/API assembly and HTTP-facing adapters. `src/web/canonical_app.py` is the current canonical API assembly boundary; production runtime ownership still requires runtime/deployment evidence.

### `src/core/`

Configuration and platform-level foundational components. It must not become a second business-logic layer.

### `src/models/`

Application/data models where a distinct responsibility remains justified. Duplicate representations of canonical domain concepts must be reconciled.

## 5. Access surfaces

Janavani supports independent access surfaces including Dynamic Web/WebApp, Android, iOS, Telegram Bot, Telegram Mini App, WhatsApp, Messenger, APIs and DApp/Web3 interfaces.

A surface may have interface-specific presentation/state handling, but shared Case, evidence, authority, document, consent, policy, AI and lifecycle logic belongs in shared infrastructure.

## 6. Shared capability families

Current/future shared capabilities include:

- Case and civic-action lifecycle;
- identity, authentication, authorization and consent;
- issue understanding and jurisdiction;
- authority/responsibility resolution;
- evidence and provenance;
- documents and templates;
- submission, acknowledgement and tracking;
- follow-up, RTI, appeal and escalation;
- government information and schemes;
- corrections and expert/volunteer/institution review;
- AI, RAG and Agentic AI;
- notifications and audit;
- privacy, data classification and local-first storage;
- SOS and resilient transport;
- decentralized/Web3 providers where justified.

## 7. Provider rule

Providers such as PostgreSQL, Supabase, Ollama, cloud AI, messaging systems, government APIs, Freenet, Nostr, Nym, Reticulum, blockchain and decentralized storage are adapters/providers. They must not become the canonical domain model or an accidental universal dependency.

## 8. Storage rule

Private user data is local-first where practical. Evidence originals remain local unless an explicitly authorised operation requires transmission. Persistent shared data must have a documented owner. No storage migration is approved merely because a new repository or schema exists.

## 9. Tests

`tests/` is the verification boundary. Tests should cover domain behavior, workflows, repositories, integrations, privacy/security policies, architecture invariants, failure isolation and end-to-end citizen journeys as capabilities mature.

A test file existing is not evidence that its tests passed.

## 10. Documentation

Use `docs/DOCUMENTATION_INDEX.md` as the documentation authority map. Use `docs/AI_HUMAN_DEVELOPER_CONTEXT.md` for concise orientation. Use the latest Master Task Checklist status register for execution state.

## 11. Archive

Historical code/documentation may be retained under `archive/` for traceability. Before moving code or documentation, verify dependencies, replacement ownership, runtime references and historical value. Archive first; delete only after evidence.

## 12. New-code rule

Before creating a new module:

1. Search for an existing owner.
2. Check the capability registry and contracts.
3. Check imports and tests.
4. Determine whether the proposed module is shared infrastructure or interface-specific.
5. Prefer extending/converging an existing implementation.
6. Create a new boundary only when responsibility is genuinely distinct.
7. Document the decision when architecture changes materially.

## 13. Current implementation direction

Rust is the canonical long-term domain/core direction. Python remains appropriate at application/integration edges during controlled migration. The Dynamic Web may use a hybrid public-Web + rich WebApp architecture. These are implementation choices inside one Janavani ecosystem.

## 14. Canonical conclusion

**One ecosystem. One canonical civic domain and lifecycle. Shared infrastructure and capabilities. Independent interfaces. Replaceable providers. User-controlled capability invocation. Privacy and safety by design and default. Verified implementation rather than documentation-only completion.**
