# Janavani Master Execution Register

**Status:** Active engineering control document  
**Audit date:** 2026-10-10  
**Repository:** `netzen-abm/janavani`  
**Verified main snapshot:** `0fb4c50d188811bed700555e1ed82735adef790e`  
**Integration vehicle:** [PR #203](https://github.com/netzen-abm/janavani/pull/203)  
**Branch invariant:** exactly nine active branches; do not create another branch for this work.

## Operating decision

Stop adding architecture layers unless an existing boundary cannot satisfy a demonstrated requirement. Prefer implementation, integration tests, real runtime checks, failure tests, and evidence. Split only at independent change, trust, persistence, provider, deployment, or reuse boundaries. Preserve cohesion when splitting would duplicate orchestration or weaken invariants.

## Live baseline verified on 2026-10-10

- [x] Default branch is `main`.
- [x] Exactly nine remote branches are listed; all match the approved branch set below.
- [x] Main commit `0fb4c50d188811bed700555e1ed82735adef790e` has successful CI, Security CI, Docker, Architecture Guard, branch-budget, test, and build checks at audit time.
- [x] Recursive Git tree returned 915 files (not truncated): 284 under `src/`, 153 under `tests/`, 173 under `archive/`, and 225 under `docs/`.
- [x] Active-source line ceiling is enforced in CI by `scripts/check_code_line_limits.py --limit 180`.
- [ ] Do not equate passing CI with production readiness; complete the runtime, security, recovery, and deployment gates below.
- [ ] PR #203 must be refreshed/revalidated against current `main` before merge. Its observed check set includes failed security/deployment checks and Python 3.10 build failure on the prior run. Re-run checks after branch synchronization; do not merge based on mergeability alone.
- [ ] Branch protection is not enabled on the nine listed branches in the branch metadata observed during this audit. Verify repository rulesets and establish enforceable required checks without changing the branch count.

## Approved nine branches — exact set

- [x] `main`
- [x] `integration/canonical-platform`
- [x] `audit/postgres-provider-production-gates`
- [x] `chore/ecosystem-shared-capability-infrastructure`
- [x] `feat/canonical-capability-execution-envelope`
- [x] `feat/canonical-case-kernel`
- [x] `feat/canonical-civic-action-vertical-slice`
- [x] `feat/canonical-sos-contract`
- [x] `feat/capability-scoped-consent-agent-enforcement`

**Branch rule:** preserve exactly this set. Before retiring any branch, compare its unique commits/files against `main`, retain evidence, selectively cherry-pick or merge useful changes into an existing approved branch, run required checks, verify the resulting tree, then delete only the redundant ref. Never create a temporary branch.

## Code-level audit findings with source references

### P0 — production blockers

- [ ] **Durable private Case content and cross-surface continuity.** `src/platform/surface_case_composition.py:126-134` selects `InMemoryCaseContentRepository` by default; `src/storage/repositories/case_content.py:36-52` confirms it is transient process memory. Case metadata may be durable while narrative/claims are lost on restart or unavailable to another independently composed surface. Implement an explicitly selected, least-privilege content provider or a genuinely device-owned encrypted design; document the exact privacy/data-flow decision, retention, deletion and authorization. Do not silently centralize sensitive data.
- [ ] **Real cross-surface identity pairing.** `src/identity/linking.py:19-57` provides durable identity-link storage, and `src/identity/linking.py:91-100` fails closed for unknown/unverified links. This is not itself proof of a short-lived, single-use, replay-resistant Web↔Telegram pairing ceremony. Implement the pairing flow with expiry, one-time consumption, rate limits, explicit user confirmation, authenticated principal binding, audit metadata, and negative tests.
- [ ] **Independent surface runtime proof.** `src/bot_telegram.py:23-66` composes Telegram services and registers the current handlers; `src/web/civic_case_router.py:21-44` exposes authenticated Case creation/retrieval. Add runtime tests showing one citizen's Case can be resumed across separately running Web and Telegram processes using durable providers, while a different principal is denied.
- [ ] **Production provider gates.** Re-run live PostgreSQL authorization/RLS tests using least-privilege roles, concurrent/idempotent operations, restart recovery, outage/degraded behavior, and backup/restore. Confirm runtime configuration matches `docs/architecture/ENVIRONMENT_CONTRACT.md:70-110`; no production fallback to in-memory persistence.
- [ ] **Submission remains fail-closed.** `src/platform/surface_case_composition.py:49-53` defines a transport that refuses unconfigured external delivery. Preserve this. Verify generated documents are review/download/self-send by default; any future external submission must be a separate, explicit, auditable consequential operation.

### P1 — complete the real citizen journey

- [ ] Case create/list/read/update and lifecycle transitions, with ownership checks on every operation.
- [ ] Authority discovery with source URL, retrieval time, jurisdiction and confidence; prevent unsupported authority claims.
- [ ] Evidence capture and local-first handling: file type/size validation, hash, metadata/EXIF handling, preview, deletion verification, provenance, and explicit approval before any transmission.
- [ ] Document drafting, review/correction, PDF and DOCX export, and regression tests for rendering.
- [ ] Consent scoped to action, data, purpose, recipient/provider and duration; refusal must preserve a non-AI/non-sharing path.
- [ ] Tracking, acknowledgement, follow-up, escalation and citizen verification of outcomes.
- [ ] Full Telegram workflow: guided case creation, authority, evidence references, document review/export, consent, My Cases, tracking, help, privacy and recovery. Keep Telegram-specific interaction in adapters; do not duplicate domain logic.
- [ ] Full WebApp workflow: authenticated workspace, case list/detail, guided action, authority, evidence, document preview/export, status history and recovery UX.
- [ ] Mini App is a separate adapter over the same capabilities; do not block core Web/Telegram completion on it.

### P1 — security, privacy and trust

- [ ] Verify every protected API route has authenticated identity plus object-level authorization; test IDOR/cross-user access.
- [ ] Ensure logs/telemetry contain no personal narrative, evidence, tokens, secrets or sensitive identifiers.
- [ ] Verify external AI/agent providers receive only explicitly permitted, minimized context; non-AI paths remain complete.
- [ ] Require user confirmation for consequential actions and prevent agents from gaining authority through provider installation.
- [ ] Verify consent revocation, data export/deletion, key/recovery lifecycle and device migration before claiming local-first encryption production-ready.
- [ ] Test Telegram privacy realities: bot messages and files are handled by Telegram infrastructure; do not claim that Telegram transport provides Janavani-controlled end-to-end confidentiality. Keep sensitive evidence on-device where feasible and direct users to the protected Web/Mini App flow when needed.

### P2 — repository quality and operational readiness

- [ ] Run the canonical full test suite and record test count/results against the exact commit.
- [ ] Make static analysis actionable: remove `continue-on-error: true` from lint only after baseline is remediated and CI is clean.
- [ ] Review eager repository factory evaluation in `src/platform/surface_case_composition.py:103-124,141-143`: `dict.setdefault(key, factory())` evaluates the factory even when the key exists. Replace with explicit get/create only if tests show duplicate construction or side effects; avoid a cosmetic refactor.
- [ ] Verify all active source files remain within the CI line ceiling and split only at meaningful boundaries.
- [ ] Reconcile the active master register, capability catalogue, ADRs and deployment map; historical checklists remain archived and are not competing sources of truth.
- [ ] Verify secrets, dependency pins, container image, health/readiness behavior, deploy rollback, backup retention and restore drills.
- [ ] Re-check all nine branches and PR state after every integration wave.

## Parallel execution lanes

### Lane A — shared core and persistence
- [ ] Finish the durable Case-content boundary without violating the local-first privacy contract.
- [ ] Prove PostgreSQL atomicity, authorization/RLS, idempotency and restart behavior.
- [ ] Keep Case lifecycle and policy semantics channel-neutral.

### Lane B — WebApp
- [ ] Complete authenticated case workspace and lifecycle UI against canonical API contracts.
- [ ] Add browser E2E for create → authority → evidence reference → draft → review/export → tracking.
- [ ] Verify failure/degraded behavior and ensure the UI never reports an unverified external submission as complete.

### Lane C — Telegram
- [ ] Complete guided flows using the same capabilities and durable repositories.
- [ ] Implement secure account/case pairing with explicit confirmation and single-use expiring tokens.
- [ ] Add Telegram runtime tests and verify the bot remains usable if Web is unavailable (and vice versa).

### Lane D — release assurance
- [ ] Refresh PR #203 against current `main`; resolve CI/security/deployment failures.
- [ ] Run live RLS, restart/outage, backup/restore and cross-surface tests.
- [ ] Publish a truthful release evidence report; merge only when all required gates pass.

## Definition of done

A capability is not complete because a contract or UI exists. It is complete only when the implementation, provider behavior, authorization/privacy enforcement, tests, cross-surface integration, failure behavior, operational configuration and documentation are verified against the same commit.

**Immediate next two steps**

1. Fix and prove durable Case-content semantics plus Web↔Telegram identity pairing; these are the highest-risk blockers to meaningful cross-surface continuity.
2. Refresh PR #203 against current `main`, run the complete CI/security/runtime gates, and merge only with evidence.
