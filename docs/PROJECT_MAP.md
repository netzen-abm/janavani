# JANAVANI — PROJECT MAP

**Status:** ACTIVE — REPOSITORY NAVIGATION AND OWNERSHIP MAP
**Version:** 2.1
**Date:** 25 October 2026

## 1. Purpose

This document explains where production code, interfaces, shared capabilities, storage, tests and documentation belong. It is a navigation/ownership document, not a replacement for `docs/SOURCE_OF_TRUTH.md` or `docs/JANAVANI_MASTER_ARCHITECTURE.md`.

## 2. Repository model

```text
janavani/
├── src/                 # primary application source
├── crates/              # Rust core/application workspace
├── tests/               # automated verification
├── docs/                # active documentation
├── planning/            # active detailed contracts/specifications
├── archive/             # historical/superseded material
├── database/            # repository data/seeds/reference assets
├── db/                  # SQL migrations and persistence schema
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

## 2A. Current source layout (verified 25 October 2026)

The current tree is organized around these existing directories. Names below describe observed repository responsibilities; they do not claim every module is production-ready.

```text
src/
├── platform/       # shared provider/capability composition
├── capabilities/   # reusable capability contracts and behavior
├── core/           # domain primitives, lifecycle and execution context
├── identity/       # verified identities, external links and pairing
├── access/         # authorization, consent and capability gates
├── security/       # cross-cutting security utilities/policies
├── storage/        # provider selection, repositories and transactions
├── documents/      # document drafting/rendering and artifact contracts
├── delivery/       # explicit delivery/submission contracts
├── ai/             # AI providers, routing and shared AI gateway
├── adapters/       # surface and provider adapters, including Telegram identity
├── commands/       # Telegram command handlers delegating to shared capabilities
├── conversation/   # cohesive Telegram conversation state machine
├── web/            # FastAPI API assembly, HTTP routers, Telegram webhook/worker
├── webapp/         # interactive citizen UI, OIDC/session gateway and API client
├── config/         # runtime configuration/validation
├── services/       # compatibility/transitional services; migrate selectively
├── app/, utils/    # bootstrap and supporting utilities; inspect before moving
├── migration/      # migration-related helpers; distinguish from db/migrations
├── database/       # in-source data/compatibility modules where present
├── web_dioxus/     # excluded from Cargo workspace; not the deployed API
├── web_mvp/        # compatibility surface retained pending import/runtime proof
└── whatsapp/       # additional messaging-surface work; verify before claiming deployed
```

Rust workspace:
- `crates/janavani-core/` — Rust core crate.
- `crates/janavani-application/` — Rust application crate.
- `Cargo.toml` defines the current workspace. No Cargo.lock was present in the reviewed branch at the time of this audit.

Repository-level persistence and verification:
- `db/migrations/` — SQL schema/migration evolution.
- `database/` — root data/reference assets; do not conflate this with SQL migrations.
- `tests/` — Python unit, contract and integration verification.
- `.github/workflows/` — CI, architecture, security, container and branch retirement automation.
- `render.yaml` — proposed service definitions; not proof of deployed service inventory.
- `archive/` — preserved historical generations, assets, branch heads, documentation and retired dependencies.

Historical generations are retained under `archive/generations/`; quarantined obsolete placeholders are retained under `archive/legacy/quarantined/`. Do not re-create the absent `src/domain/`, `src/workflow/`, `src/engine/`, or `src/models/` namespaces just to match old documentation. The canonical domain/capability ownership currently resides primarily in `src/core/` and `src/capabilities/`, while workflow/session mechanics are separated by actual use case and adapter boundary.

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

### `src/platform/`
Shared composition roots and dependency graphs. Resolve provider choice once and share a consistent capability/repository graph across independent surfaces.

### `src/capabilities/`
Canonical, reusable capability contracts and behavior (Case, Evidence, Authority, Consent, Document, Civic Action and related lifecycle operations). Surface adapters should call these owners instead of implementing alternate business rules.

### `src/core/`
Stable domain objects, lifecycle invariants, transaction/idempotency contracts and execution-context primitives. Keep rules cohesive when they protect the same invariant.

### `src/identity/`, `src/access/`, and `src/security/`
Identity verification/linking, authorization, consent and cross-cutting security policy. A Telegram transport ID or browser-supplied value is not automatically a trusted citizen principal.

### `src/storage/`
Provider-neutral repository contracts, PostgreSQL implementations, provider composition and Unit-of-Work/transaction semantics. Database/provider mechanics must not leak into the UI.

### `src/documents/` and `src/delivery/`
Document composition and artifact handling are separate from external delivery. Janavani must not claim that a document was submitted or received without the appropriate confirmed acknowledgement.

### `src/ai/`
Replaceable AI providers and shared execution/routing. AI is optional assistance, not the source of truth for identity, facts, consent or consequential decisions.

### `src/web/`
Canonical FastAPI composition and HTTP adapters. The same directory currently also contains the Telegram webhook and inbox worker entry points; these are separate runtime/trust responsibilities despite sharing a package namespace. Preserve the existing entry paths until deployments/imports/tests are deliberately migrated.

### `src/webapp/`
Interactive WebApp presentation, OIDC authorization-code/PKCE flow, session handling, request-scoped API client, authority intake and Case workspace. Keep browser identity separate from API identity assertions; verify production issuer/session/revocation settings before release.

### `src/adapters/`, `src/commands/`, and `src/conversation/`
Telegram identity/provider adapters, command handlers and the cohesive conversation state machine. Do not split the conversation engine by arbitrary file size; extract only independent transport, trust, persistence or lifecycle boundaries.

### `src/services/`, `src/app/`, `src/utils/`, and `src/migration/`
Compatibility, application bootstrap and supporting modules. Their ownership must be confirmed file-by-file before migration; do not move the mixed service directory wholesale.

### `src/web_dioxus/`, `src/web_mvp/`, and `src/whatsapp/`
Non-primary/compatibility or developing surfaces. Their presence in the tree does not make them the deployed canonical API or a production-ready channel. Preserve until imports, test references and runtime status are verified.

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

Use `docs/DOCUMENTATION_INDEX.md` as the documentation authority map. Use `docs/AI_HUMAN_DEVELOPER_CONTEXT.md` for concise orientation. Use `docs/MASTER_TASK_CHECKLIST.md` plus the current dated rebaseline `docs/90-audits/2026-10-25-engineering-proof-cycle-and-repository-structure-audit.md` for execution state. Older date-stamped findings remain historical where the current rebaseline explicitly supersedes them.

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
