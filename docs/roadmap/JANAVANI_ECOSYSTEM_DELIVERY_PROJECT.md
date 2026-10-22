# Janavani Ecosystem Delivery Project

## Objective
Deliver a secure, reliable citizen-participation platform in which the WebApp and Telegram bot are independent access surfaces over canonical shared capabilities. Optimize for verified end-to-end behavior, privacy, recoverability, and maintainability—not architecture churn.

## Product boundaries
- WebApp and Telegram are independent adapters and deployment/runtime surfaces.
- Case, Evidence, Authority, Consent, Document, Submission, identity policy, and audit semantics belong to shared capabilities where they have multiple consumers.
- Persistence implementations and external providers stay behind explicit contracts.
- Keep orchestration cohesive where splitting it would duplicate transaction or lifecycle invariants.
- Do not introduce a new service or abstraction without a concrete boundary, independent lifecycle, trust boundary, provider dependency, or demonstrated reuse need.

## Release gates — ordered
1. **Reliability first:** diagnose and fix the isolated Telegram inbox worker hang; run the worker test repeatedly and then run the canonical suite.
2. **PostgreSQL durability:** prove crash-after-commit/replay against real PostgreSQL, including idempotency, single durable business effect, stale-worker fencing, and terminal inbox acknowledgement.
3. **Cross-surface identity and Case continuity:** create/read the same authorized Case from Web and Telegram, test unauthorized cross-user access, and verify fresh-process identity resolution.
4. **Complete citizen vertical slice:** Case intake → authority selection → evidence/document references → review → submission preparation → acknowledgement/status tracking. Do not claim external submission succeeded unless an external receipt proves it.
5. **Independent runtime operation:** verify Web/API and Telegram service startup, readiness, failure isolation, retry/recovery, and configuration.
6. **Security and privacy:** least-privilege database roles, tenant/owner authorization, consent checks, minimal payload retention, secret scanning, and safe logging.
7. **Performance:** measure API latency, query counts, inbox lag/retry rate, duplicate/replay rate, and resource usage before optimizing.

## Workstreams
- **W1 — Worker reliability:** one isolated test reproducer, bounded test timeout, diagnostic output, cancellation-safe cleanup, repeated run.
- **W2 — Persistence correctness:** real PostgreSQL crash/replay and transaction rollback/concurrency gates.
- **W3 — Shared capability vertical slice:** canonical Case/Submission contracts reused by Web and Telegram; no parallel business logic.
- **W4 — WebApp:** authenticated identity, Case creation and retrieval, evidence/document lifecycle, review, status timeline, accessibility and responsive UX.
- **W5 — Telegram bot:** webhook durability, command/state flow, safe error messages, retries/dead letters, cancellation semantics, identity pairing and Case continuity.
- **W6 — Operations:** independent service deployment, health/readiness, migrations, backups/restore, observability and incident runbook.
- **W7 — Repository hygiene:** exactly nine active branches; archive evidence before retiring a branch; never merge/delete based on branch count alone.

## Definition of done
- Targeted tests pass repeatedly and the canonical suite passes.
- Live PostgreSQL integration gates pass; skipped tests are reported as skipped, never as proof.
- Architecture, security, dependency, and container checks pass.
- Web and Telegram share authorized business state without sharing failure fate.
- Every material claim is backed by CI, runtime, or reproducible integration evidence.
- PR stays draft until the required gates are evidenced.

## Delivery issue map
- Master project tracker: [Issue #207](https://github.com/netzen-abm/janavani/issues/207)
- W1 reliability and PostgreSQL replay: [Issue #208](https://github.com/netzen-abm/janavani/issues/208)
- W4 authenticated WebApp Case lifecycle: [Issue #209](https://github.com/netzen-abm/janavani/issues/209)
- W5 Telegram citizen journey: [Issue #210](https://github.com/netzen-abm/janavani/issues/210)
- W6 shared infrastructure production readiness: [Issue #211](https://github.com/netzen-abm/janavani/issues/211)

## Proposed delivery phases
These are planned acceptance phases, not a claim that GitHub milestones have been created:
1. **Reliability baseline:** worker cancellation, isolated regression tests, PostgreSQL crash/replay.
2. **Citizen vertical slice:** shared identity and Case continuity; evidence/document, review, submission state and acknowledgement.
3. **Operational readiness:** independent deployments, least-privilege database roles, RLS/ownership, backups and recovery.
4. **Measured optimization:** use baseline latency, query counts, queue lag, retries and resource measurements to choose targeted optimizations.

## Current checkpoint — 2026-10-22
- Live branch inventory: nine sanctioned branches.
- Latest inspected previous run: Docker build, Architecture Guard, secret/privacy scan, dependency review and branch-budget gate passed; the isolated worker test timed out.
- Diagnostic trace located the hang during the worker regression test and showed the test was not completing after cancellation. The worker cleanup previously awaited child tasks while catching `CancelledError` broadly. Cleanup now uses `asyncio.gather(..., return_exceptions=True)` to preserve cancellation of the worker itself; this is a root-cause fix candidate pending CI confirmation.
- Regression tests no longer block an executor thread waiting on a `threading.Event`; they poll asynchronously with a bounded deadline.
- Isolated test CI has verbose output and a faulthandler timeout enabled.
- PostgreSQL crash-after-commit/replay test now terminates a child process after the transaction returns and before the inbox is marked processed; execution is still unverified.
- Current CI runs for the latest checkpoint were queued at last inspection. Do not treat them as passing.
- PR #204 remains draft. Do not merge until worker regression, canonical suite, live PostgreSQL and remaining release gates are evidenced.
