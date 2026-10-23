# Janavani Ecosystem Delivery Project

## Objective
Deliver a secure, reliable citizen-participation platform in which the WebApp and Telegram bot are independent access surfaces over canonical shared capabilities. Optimize for verified end-to-end behavior, privacy, recoverability, and maintainability—not architecture churn.

## Product boundaries
- WebApp and Telegram are independent adapters and deployment/runtime surfaces.
- Case, Evidence, Authority, Consent, Document, Submission, identity policy, and audit semantics belong to shared capabilities where they have multiple consumers.
- Persistence implementations and external providers stay behind explicit contracts.
- Keep orchestration cohesive where splitting it would duplicate transaction or lifecycle invariants.
- Do not introduce a new service or abstraction without a concrete boundary, independent lifecycle, trust boundary, provider dependency, or demonstrated reuse need.
- Citizen-content privacy is a data contract: minimal Case metadata must not accidentally destroy content that the authorized citizen must later retrieve. Keep content retention in an explicitly approved, access-controlled provider; do not persist narrative into metadata by default.

## Release gates — ordered
1. **Worker reliability:** isolate and fix Telegram inbox worker hangs; run the worker regression repeatedly with bounded timeouts, then run the canonical suite.
2. **PostgreSQL durability:** prove crash-after-commit/replay against real PostgreSQL, including idempotency, one durable business effect, stale-worker fencing, terminal inbox acknowledgement, rollback, and concurrent updates.
3. **Cross-surface identity and Case continuity:** create/read the same authorized Case from Web and Telegram, test unauthorized cross-user access, and verify fresh-process identity resolution.
4. **Citizen content privacy and recoverability:** define metadata versus citizen-content fields; prove authorized retrieval after process restart, owner isolation, retention/deletion behavior, and transactional consistency of content references.
5. **Complete citizen vertical slice:** Case intake → authority selection → evidence/document references → review → explicit consent → submission preparation → acknowledgement/status tracking. Never claim external submission succeeded unless an external receipt proves it.
6. **Independent runtime operation:** verify Web/API and Telegram service startup, readiness, failure isolation, retry/recovery, configuration, and deployment.
7. **Security and privacy:** least-privilege database roles, owner authorization/RLS, consent checks, minimal payload retention, secret scanning, safe logging, CSRF protection and trusted identity assertion validation.
8. **Measured performance:** measure API latency, query counts, inbox lag/retry rate, duplicate/replay rate, and resource usage before optimizing.

## Workstreams
- **W1 — Worker reliability:** isolated reproducer, bounded timeout, diagnostic output, cancellation-safe cleanup, repeated run.
- **W2 — Persistence correctness:** real PostgreSQL crash/replay, transaction rollback, concurrency, ownership and restart gates.
- **W3 — Shared capability vertical slice:** canonical Case/Submission contracts reused by Web and Telegram; no parallel business logic.
- **W4 — WebApp:** authenticated identity, Case creation/retrieval, evidence/document lifecycle, review, status timeline, accessible/responsive UX and safe artifact handling.
- **W5 — Telegram bot:** webhook durability, guided civic-action flow, safe error messages, retries/dead letters, cancellation semantics, identity pairing and Case continuity.
- **W6 — Operations:** independent service deployment, health/readiness, migrations, backups/restore, observability and incident runbook.
- **W7 — Repository hygiene:** immediate target exactly eight physical active branches; eventual target only `main`. Archive and verify unique work before retirement. Never merge/delete based on branch count alone. Update the CI branch-count guard only after the live physical count has been verified at eight.
- **W8 — Case data contract:** tracked by [Issue #212](https://github.com/netzen-abm/janavani/issues/212); preserve metadata minimization while ensuring the citizen can retrieve approved content they own.

## Definition of done
- Targeted tests pass repeatedly and the canonical suite passes.
- Live PostgreSQL integration gates pass; skipped tests are reported as skipped, never as proof.
- Architecture, security, dependency, and container checks pass.
- Web and Telegram share authorized business state without sharing failure fate.
- A citizen can retrieve retained Case content after a fresh process starts; another principal cannot.
- Every material claim is backed by CI, runtime, or reproducible integration evidence.
- PR #204 stays draft until required gates are evidenced.

## Delivery issue map
- Master project tracker: [Issue #207](https://github.com/netzen-abm/janavani/issues/207)
- W1 reliability and PostgreSQL replay: [Issue #208](https://github.com/netzen-abm/janavani/issues/208)
- W4 authenticated WebApp Case lifecycle: [Issue #209](https://github.com/netzen-abm/janavani/issues/209)
- W5 Telegram citizen journey: [Issue #210](https://github.com/netzen-abm/janavani/issues/210)
- W6 shared infrastructure production readiness: [Issue #211](https://github.com/netzen-abm/janavani/issues/211)
- W8 Case privacy and recoverability contract: [Issue #212](https://github.com/netzen-abm/janavani/issues/212)

## Delivery phases
These are acceptance phases, not a claim that GitHub milestones have been created:
1. **Reliability baseline:** worker cancellation, isolated regression tests, PostgreSQL crash/replay.
2. **Citizen vertical slice:** shared identity and Case continuity; privacy-preserving content retrieval; evidence/document, review, submission state and acknowledgement.
3. **Operational readiness:** independent deployments, least-privilege database roles, RLS/ownership, backups and recovery.
4. **Measured optimization:** use baseline latency, query counts, queue lag, retries and resource measurements to select targeted optimizations.
5. **Branch convergence:** retire one verified branch at a time, reducing 9 → 8 → fewer → only `main`; do not bulk-merge heavily diverged branches merely to retire them.

## Current checkpoint — 2026-10-23
- Live branch inventory returned nine physical refs: `audit/postgres-provider-production-gates`, `chore/ecosystem-shared-capability-infrastructure`, `feat/canonical-capability-execution-envelope`, `feat/canonical-case-kernel`, `feat/canonical-civic-action-vertical-slice`, `feat/canonical-sos-contract`, `feat/capability-scoped-consent-agent-enforcement`, `integration/canonical-platform`, and `main`.
- Immediate target is exactly eight; the target is not yet met. The connected GitHub actions currently available in this session do not expose a branch-delete operation. Do not simulate deletion by moving a ref. Use an authorized deletion operation and re-query the live inventory.
- Comparisons show several feature branches are heavily diverged from `main`; do not merge them wholesale. Extract reviewed, still-valid changes and verify archived snapshots before retiring source branches.
- PR #204 remains draft. Previously inspected CI, Security CI, Docker, Architecture Guard, Dependency Review and deployment checks reported success for the candidate commit, but those results do not prove production readiness or current end-to-end acceptance.
- The PostgreSQL Case codec currently replaces the subject with Case type and stores an empty narrative; the existing fake-repository test explicitly expects this. Do not alter the mapping blindly. Define the metadata/content contract and prove owner-scoped content recovery against real PostgreSQL.
- The WebApp and Telegram must pass cross-process continuity, authorization, replay/idempotency, restart recovery, and complete citizen vertical-slice gates before PR promotion.
