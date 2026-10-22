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

## Current checkpoint — 2026-10-22
- Live branch inventory: nine sanctioned branches.
- Docker build and Architecture Guard: passed on the latest inspected run.
- Secret/privacy scan and dependency review: passed on the latest inspected run.
- Isolated Telegram worker regression gate: timed out after 30 seconds; root-cause diagnosis is the immediate blocker.
- Canonical suite: still in progress at last inspection.
- PostgreSQL crash-after-commit/replay test: added to the existing integration test file; execution result not yet verified.
- PR #204 remains draft. Do not merge until the failed worker gate and remaining release gates are resolved.
