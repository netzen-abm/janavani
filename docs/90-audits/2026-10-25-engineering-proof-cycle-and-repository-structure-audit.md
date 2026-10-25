# Janavani Engineering Proof Cycle and Repository Structure Audit

**Date:** 25 October 2026  
**Status:** Review baseline; not a production acceptance certificate  
**Repository:** `netzen-abm/janavani`  
**Working review line:** `chore/ecosystem-shared-capability-infrastructure`

## Executive decision

Converge and verify the existing implementation before adding abstractions or expanding surfaces. Keep WebApp and Telegram as independent adapters over shared capabilities. Preserve cohesive domain/lifecycle/transaction logic; split only at change, trust, persistence, provider, independent runtime, or independent reuse boundaries.

The full ecosystem scope remains unchanged. This review focuses on the first production-quality civic-action slice and the infrastructure contracts that future surfaces can reuse.

## Live inventory

At review time:

- GitHub default branch: `main`.
- Physical branch inventory: **9 refs**, not the required 8.
- PR #204 remains open and draft; its latest inspected head was `7799850ad0ceede7386364e8ccb4e334f74fdd83`.
- PR #213 remains open; its latest inspected head was `d036839730968771e0db6d043eb2c85ad9531a88`.
- PR #204's earlier head `449b483cc1da7a15f9b4dcbd418630ed692cfc57` had seven successful workflow runs. Later OIDC changes at `7799850ad0ceede7386364e8ccb4e334f74fdd83` must be evaluated on their own exact-SHA checks; previous green runs do not certify the later head.
- The active `main` ruleset (ID `25706799`) showed zero required approving reviews, no required Code Owner review, no required review-thread resolution, and non-strict required status checks. This differs from the written governance rule requiring an independent approval.
- The connected Render account showed one live service, `JanaVani`, using `uvicorn src.web.canonical_app:app --host 0.0.0.0 --port $PORT`. Proposed `render.yaml` definitions for the separate WebApp and Telegram webhook are not proof of deployment.

## Priority release blockers

### P0.1 — Branch policy and retirement

- Correct the live ruleset so independent review matches the written governance policy.
- Do not merge PR #213 until independent review and the required checks are valid.
- Allow the guarded post-merge workflow to archive the exact transition-branch head, delete its ref, and verify the physical inventory is exactly eight.
- Re-query GitHub after deletion. Do not claim compliance from a green PR alone.
- Keep the eventual one-branch goal (`main` only) gated on full product-readiness evidence; archive useful work before retiring feature branches.

### P0.2 — Telegram inbox privacy/retention

The current `PostgresTelegramInbox.accept` stores the full Telegram update JSON in the durable inbox. A text update may contain raw citizen narrative and identifiers. The inbox payload is cleared after successful processing or terminal dead-lettering, but can remain during pending, processing, and retry states.

This means the Case table's metadata-only persistence rule does not by itself establish that citizen narrative never enters durable Janavani storage. Issue #219 tracks the decision.

Required response:
- define precisely which fields may be durably retained;
- define maximum retention and deletion behavior for success, retry, and dead-letter;
- review encryption/key management, least-privilege database access, logging and telemetry;
- cover text, captions, attachments, contact/location, and other structured updates;
- align the user-facing privacy notice with actual Telegram and Janavani processing;
- add PostgreSQL-backed negative tests proving prohibited fields do not persist, or prove the approved encrypted/TTL policy.

Do not silently centralize raw citizen content to obtain workflow continuity.

### P0.3 — Replay safety

Telegram delivery is at-least-once. Existing code has inbox deduplication and lease fencing, while durable Case/Submission repositories have idempotency mechanisms. These components do not alone prove that an already-committed business effect remains unique if a worker dies before marking the inbox row processed.

Issue #217 requires a real PostgreSQL test through the handler/capability path, failure injection after commit, replay through a fresh worker/repository, durable projection/version/event assertions, conflicting idempotency-key rejection, and eventual inbox completion.

Reuse the current durable transaction/idempotency boundaries; do not add a second generic idempotency framework.

### P0.4 — WebApp identity and independent deployment

The working branch describes an OIDC authorization-code flow with PKCE, state/nonce validation, JWKS validation, short-lived internal API assertions, secure cookie settings and a liveness route. The actual issuer/client/session configuration and end-to-end flow still need deployment evidence.

The currently observed Render inventory contains only the canonical API service. Deploy and test the WebApp, API, and Telegram webhook as independent runtimes before describing the end-to-end ecosystem as product-ready.

The current Web session is a signed stateless cookie with a bounded lifetime; logout clears the local cookie but cannot revoke a copied cookie server-side. Implement/test shared revocation or explicitly accept this bounded residual risk before product-ready release for sensitive citizen data.

### P0.5 — Reproducible build/type/lint gates

Issue #218 tracks:
- one authoritative Python dependency-lock strategy, compatible with the current deployment commands;
- a Cargo.lock decision appropriate to the repository's Rust workspace and application use;
- `cargo test --workspace --locked` alongside `cargo check` and Clippy;
- a Ruff baseline followed by required clean/changed-code gates;
- selective static type checking at high-risk boundaries (identity, domain/application contracts, repository interfaces).

Do not maintain competing lock sources or turn this into an unscoped legacy rewrite.

## Current architecture map

The source tree already contains the meaningful boundaries:

| Responsibility | Canonical path(s) | Responsibility and audit note |
|---|---|---|
| Canonical HTTP API composition | `src/web/canonical_app.py` | FastAPI app assembly, router registration and health/version routes. |
| HTTP surface adapters | `src/web/*_router.py` | Request parsing, identity dependency and HTTP response semantics; should not own domain rules. |
| Interactive WebApp | `src/webapp/main.py`, `src/webapp/*` | Presentation and request-scoped API client; separate runtime from API is intended and must be deployed/tested. |
| WebApp identity boundary | `src/webapp/*oidc*`, identity/session modules | Browser authentication/session trust boundary. Verify actual configured issuer and server-side revocation policy. |
| Telegram composition/handlers | `src/bot_telegram.py`, `src/commands/*`, `src/conversation/*` | Telegram transport, conversation state and handler orchestration. Raw narrative is currently transient in process memory except the durable webhook inbox payload. |
| Telegram webhook/inbox worker | `src/web/telegram_webhook_app.py`, `src/web/telegram_inbox_worker.py` | Durable ingress, update validation, claim/lease, retry and dispatch. Full-update persistence is the privacy issue in P0.2. |
| Shared Case capability | `src/capabilities/civic_case*`, `src/core/civic_case.py` | Case operations, domain types, lifecycle invariants and authorization. Keep cohesive. |
| Shared civic-action capabilities | `src/capabilities/civic_action*`, Authority/Evidence/Consent/Document/Submission modules | Reusable domain services used across surfaces. One canonical owner per capability. |
| Provider composition | `src/storage/provider_composition.py`, `src/platform/composition_*.py` | Resolve provider policy once and construct a consistent dependency graph. Keep provider-specific clients out of surfaces. |
| Persistence adapters | `src/storage/repositories/*` | PostgreSQL and other repository implementations behind contracts. Transaction ownership must stay explicit. |
| AI provider boundary | `src/ai/*` | Provider adapters, shared gateway and routing; non-AI workflow must not depend on model availability. |
| Rust workspace | `Cargo.toml`, `crates/janavani-core`, `crates/janavani-application` | Typed core/application foundations. Do not claim the deployed API runs on Rust; current Render service is Python/Uvicorn. |
| Contract/architecture tests | `tests/*` | Unit, contract, integration and negative-path tests. Integration evidence must prove PostgreSQL paths were executed and not skipped. |
| SQL migrations | `db/migrations/*` | Persistence schema/security evolution. Every migration requires forward/rollback and restore evidence appropriate to risk. |
| Deploy/CI | `.github/workflows/*`, `render.yaml`, Docker files | Execution and deployment policy. Workflow green does not mean a defined service is deployed. |

### What should not be split further

- Keep Case lifecycle rules and state transitions together where they preserve the same invariants.
- Keep Submission + Case mutation inside the existing atomic transaction boundary.
- Keep the Telegram conversation state machine cohesive; only split storage/retention when the trust or persistence contract actually differs.
- Keep API route registration in the composition root; do not create new universal orchestration wrappers.
- Keep domain contracts provider-neutral; PostgreSQL-specific logic remains in repository adapters.
- Do not split functions/classes solely to satisfy a line-count target. If the 180-line guard blocks cohesive code, review the guard exception on architectural grounds rather than manufacturing fragments.

## Runtime/language/toolchain operating model

| Concern | Janavani rule |
|---|---|
| Constants/config | Native constants and typed configuration at composition/runtime boundaries; secrets never in source. |
| Functions/objects/collections/operators | Use normal Python/Rust/JavaScript constructs. Keep business rules in shared capabilities, not in interface code. |
| Data types | Rust compile-time checks; Python annotations plus runtime request validation and selectively enforced static checks; JavaScript input validation at the browser boundary. |
| User and identity | Never trust client-provided principal/actor identifiers. The API verifies the signed assertion and enforces capability/ownership policy. Telegram identity only maps to a canonical principal after explicit verified pairing. |
| Rulebook | Source of truth, ecosystem charter, master architecture, capability registry, data/consent contracts and decision records. The enforcement layer is tests, runtime validation and repository policy—not a new universal rules engine. |
| Engine | Shared domain + application/capability functions. AI is optional/replacable assistance, not authority for identity, facts, consent or consequential action. |
| Runtime | Python FastAPI/Uvicorn API; separate WebApp and Telegram processes intended. Each requires independent health, configuration and failure tests. |
| Event loop | Async HTTP/Telegram work uses Python's async runtime; blocking repository calls must not block the event loop. Browser JavaScript has its own event loop. |
| Compiler/interpreter/JIT/transpiler | Cargo/rustc compile Rust; Python runs under its interpreter; JavaScript executes in the browser engine and may be JIT-optimized. No custom compiler/JIT/transpiler is needed. |
| Packages/build | `pyproject.toml` and `requirements.txt` for Python; `Cargo.toml` for Rust. Choose one reproducible Python lock approach and make Rust locking explicit. There is no reviewed root npm/package-lock pipeline at this baseline. |
| Verification | Syntax, tests, static analysis, Rust compilation/tests, PostgreSQL integration/RLS, backup/restore, Docker and deployment smoke checks. Record exact SHA and runtime evidence. |

## Documentation authority and file organization

The intended authority order is:

1. `NORTH_STAR.md` — purpose/outcomes.
2. Ecosystem Charter — scope and governing invariants.
3. `docs/CONSTITUTIONAL_GOVERNANCE.md` — civic/legal framing.
4. `docs/SOURCE_OF_TRUTH.md` — canonical architectural rules.
5. `docs/JANAVANI_MASTER_ARCHITECTURE.md` — architecture.
6. `docs/JANAVANI_PRODUCT_LANDSCAPE.md` — capabilities and surfaces.
7. `ROADMAP.md` — construction sequence.
8. `docs/MASTER_TASK_CHECKLIST.md` — tasks and verification status.
9. `docs/CAPABILITY_REGISTRY.md` — capability ownership/status.
10. `planning/` — active specifications/contracts.
11. `docs/architecture/`, `docs/operations/`, `docs/90-audits/` — design boundaries, runbooks and dated evidence.
12. `archive/` — historical/superseded items only; never current implementation guidance.

The repository already has this intended structure in its README, but older dated checklist sections contain conflicting branch counts and historic verification statements. Keep the record for provenance; add a dated current rebaseline that explicitly supersedes it rather than silently rewriting history.

### Proposed file organization (do not bulk-move files without import/runtime proof)

```
/
├── README.md
├── NORTH_STAR.md
├── ROADMAP.md
├── pyproject.toml
├── requirements.txt
├── Cargo.toml
├── .github/workflows/
├── src/
│   ├── web/                  # FastAPI/API composition and HTTP adapters
│   ├── webapp/               # interactive WebApp presentation/API client
│   ├── adapters/telegram/    # Telegram identity/transport adapters
│   ├── commands/             # Telegram-to-capability commands
│   ├── conversation/         # cohesive Telegram state machine
│   ├── capabilities/         # shared application capability contracts/behavior
│   ├── core/                 # domain objects/invariants
│   ├── identity/             # trust and identity linking
│   ├── access/               # authorization and consent enforcement
│   ├── storage/
│   │   ├── repositories/     # provider adapters
│   │   └── ...               # provider composition and transactions
│   ├── ai/                   # AI provider/gateway
│   └── documents/            # document generation and artifact policies
├── crates/
│   ├── janavani-core/
│   └── janavani-application/
├── db/migrations/
├── tests/
├── docs/
│   ├── architecture/
│   ├── operations/
│   └── 90-audits/
├── planning/
└── archive/
```

This is a responsibility map, not an instruction to rename established Python packages indiscriminately. Existing imports and deployed entry points must be verified before moving anything.

## Webstudio / static-site generator / Cloudflare deployment guidance

- Webstudio can be used as a visual design/export tool for the public website; it must not become the authority for Janavani business logic or authenticated Case state.
- Static HTML/CSS/JS is suitable for a public brochure/knowledge site when content and interactions do not require server-owned private state.
- The authenticated citizen workspace needs a trusted session and API boundary, so a static export alone is not the complete application runtime.
- Cloudflare Pages is suitable to evaluate for the public static site and branch/preview workflow. Workers may be considered for a specific dynamic edge requirement, but do not rewrite the current Python API simply to adopt another platform.
- Keep deployment provider configuration outside domain/capability contracts. Render/Vercel/Cloudflare are replaceable deployment adapters.
- Compare any SSG/Vercel starter by build output, runtime dependency, SSR/SSG boundary, preview isolation, headers/CSP, secrets and API integration before choosing it. Do not introduce Node/package tooling without a concrete product need.

## Ordered next two engineering actions

1. **Privacy decision and tests:** resolve full Telegram update payload persistence (Issue #219), then add a PostgreSQL-backed negative test for prohibited fields and retention/deletion behavior.
2. **Replay proof:** close Issue #217 using failure injection through the actual Telegram handler and shared Case/Submission transaction, followed by independent WebApp/API/Telegram runtime acceptance.

After those, correct branch ruleset and complete the archive-first transition to exactly eight branches, then resolve reproducible-lock/type-check gates, deploy independent services and complete the end-to-end runbook.

## Evidence standard

Do not mark a workstream COMPLETE because a file exists, a PR is mergeable, a workflow was green on an earlier SHA, or YAML describes a service. Every product-readiness claim must record implementation commit, applicable tests, security/privacy/failure results, actual service IDs and deployed commit SHAs, and a completed acceptance record.
