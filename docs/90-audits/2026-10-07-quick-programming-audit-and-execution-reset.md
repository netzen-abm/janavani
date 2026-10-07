# Janavani — Quick Programming Audit & Execution Reset — 2026-10-07

## Executive decision
Janavani is one ecosystem with shared infrastructure and independent access surfaces.

## Exactly nine active branches
1. `main`
2. `audit/postgres-provider-production-gates`
3. `chore/ecosystem-shared-capability-infrastructure`
4. `feat/canonical-capability-execution-envelope`
5. `feat/canonical-case-kernel`
6. `feat/canonical-civic-action-vertical-slice`
7. `feat/canonical-sos-contract`
8. `feat/capability-scoped-consent-agent-enforcement`
9. `integration/canonical-platform`

No tenth feature branch is authorized. Preserve useful work, verify it, integrate it, re-verify it, then retire obsolete references.

## Quick programming audit
- `src/capabilities/`: reusable capability contracts/implementations.
- `src/platform/`: shared composition/provider graph.
- `src/storage/`: repository/provider persistence.
- `src/identity/`, `src/access/`, `src/authorization/`: trust/access boundaries.
- `src/web/`: Web/API adapter and assembly.
- `src/bot_telegram.py`: Telegram bootstrap/access adapter.
- `src/core/`: canonical domain/core primitives.
- `src/documents/`: document composition/rendering.

Web and Telegram already converge on `create_surface_case_composition()`; existing cross-surface tests cover the shared Case/civic-action contract.

### Highest-value risks
1. PostgreSQL cross-user authorization/RLS evidence is not fully production-verified.
2. Restart/outage/recovery and backup/restore evidence remains open.
3. Canonical Web/API and Telegram runtime ownership still needs deployment evidence.
4. Historical/compatibility entrypoints require reachability evidence before retirement.
5. `src/capabilities/submission.py` should only be split along trust/state/delivery boundaries; do not split by arbitrary file size.
6. Some broad exception handling remains in transport/conversation paths.

## Build sequence
P0: PostgreSQL/security/runtime verification.
P1: shared civic-action vertical slice.
P2: WebApp + Telegram parity and cross-surface continuation.
P3: Mini App, messaging expansion, mobile, DApp/Web3 and resilient transports.

## Vertical slice
`issue → understand → Case → authority → evidence reference → document draft → review/correction → explicit consent → submission preparation → acknowledgement/tracking → follow-up/escalation → outcome`

## Architectural split rule
Split at boundaries of change ownership, trust/security, persistence/provider dependency, independent reuse, independently testable lifecycle/state, or external transport. Preserve cohesion when splitting would duplicate orchestration or weaken invariants.

## Definition of done
Implementation + tests + failure behavior + security/privacy verification + user workflow + documentation + commit/PR evidence + runtime/deployment evidence.


## Execution update

- WebApp API client now exposes canonical begin-submission, queue-submission and acknowledgement operations.
- WebApp Case workspace now enters the canonical review boundary instead of stopping at Case creation.
- Telegram conversation dispatch now classifies expected workflow errors and hides internal exception details from users.
- No new domain/service layer was introduced; changes remain inside existing surface adapter boundaries.
- Nine-branch invariant remains satisfied after the changes.

## Immediate next implementation gates

1. Complete WebApp review → consent → artifact → submission-preparation UI against canonical endpoints.
2. Complete Telegram document → review → consent → submission-preparation flow using the existing shared composition.
3. Add cross-surface continuation tests against a durable provider.
4. Verify PostgreSQL authorization/RLS and restart/recovery evidence before declaring durable production readiness.


## Deployment architecture confirmation

The canonical deployment configuration already keeps Web/API and Telegram as separate Render services/processes and therefore separate failure domains:

- Web/API: `uvicorn src.web.canonical_app:app`
- Telegram: `python src/bot_telegram.py`

This is the desired independence model: either surface can fail without requiring the other surface to terminate. Shared infrastructure remains below both runtimes.


## 2026-10-07 privacy convergence update

### Branch hygiene

- Exactly 9 active branches verified.
- No branch creation performed.
- No branch deletion performed because the repository already satisfies the nine-branch invariant.
- Divergent historical branches remain intentionally preserved as evidence/source material; they are not wholesale merge candidates.

### Hard privacy invariant

Janavani is not a citizen personal-data repository. Personal/sensitive citizen content is device-first and must not be durably stored by Janavani. A conventional Telegram bot necessarily receives Telegram content transiently; this is treated as transport processing, not storage permission.

### Code changes

- Telegram session no longer stores name, address, phone, email or photo fields.
- Telegram issue content uses a short-lived process-memory boundary rather than durable session state.
- Telegram Case creation now creates a metadata-only Case shell; raw narrative is not persisted.
- Case persistence adapters redact citizen subject/narrative content before storage.
- PostgreSQL transactional Case writers were aligned to the same redaction boundary.
- In-memory Case persistence follows the same contract.
- A privacy regression test was added for provider-boundary redaction.
- A controlled migration was added to scrub existing Case subject/narrative fields after backup/restore review.

### Important remaining privacy gate

Document/evidence artifact payloads and channel identity links still require a dedicated convergence pass. The target architecture is device-local content plus destination-bound transient transfer, with opaque citizen-held capability proofs preferred over durable channel-to-citizen identity graphs.
