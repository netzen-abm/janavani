# JANAVANI Ecosystem Master Task Checklist — Rebaseline
**Date:** 20 September 2026  
**Scope:** Main Janavani repository + shared-infrastructure architecture

## Executive assessment
Janavani is no longer primarily in the build-individual-features phase. The active main branch has a meaningful capability architecture, provider-neutral storage direction, PostgreSQL schema, candidate RLS, atomic Case/Submission persistence, identity propagation, and integration-test scaffolding.

Remaining work is concentrated in convergence, production evidence, shared-infrastructure hardening, runtime/deployment verification, and surface expansion.

## Phase 0 — Repository / architecture convergence
- [x] Establish canonical main repository.
- [x] Preserve legacy/Supabase implementation under archive/.
- [x] Establish capability-oriented architecture.
- [x] Establish provider-neutral repository contracts.
- [x] Establish PostgreSQL as relational standard.
- [x] Remove active runtime dependency on Supabase.
- [x] Establish canonical Action Registry.
- [x] Map actions to capability/persistence boundaries.
- [x] Document Action → Persistence → RLS dependency map.
- [ ] Finish active-code dependency sweep across imports, startup, deployment, CI and documentation.
- [ ] Verify no non-archive runtime/build Supabase dependency remains.

## Phase 1 — Data/security foundation
- [x] Canonical PostgreSQL Case schema.
- [x] Submission persistence/idempotency schema.
- [x] Evidence persistence schema.
- [x] Document artifact persistence schema.
- [x] Transaction-local principal propagation.
- [x] Case optimistic concurrency.
- [x] Atomic Submission + Case repository boundary.
- [x] Atomic Consent + Case repository contract.
- [x] PostgreSQL Consent + Case adapter.
- [x] Candidate RLS policy set.
- [x] Candidate Evidence read boundary.
- [x] Candidate Document read boundary.
- [x] FORCE RLS in candidate policy.
- [x] Candidate RLS integration test harness.
- [x] Atomic Consent transaction-boundary tests.
- [ ] Live PostgreSQL Consent + Case atomicity tests executed.
- [ ] Live PostgreSQL Evidence isolation tests executed.
- [ ] Live PostgreSQL Document isolation tests executed.
- [ ] Live PostgreSQL cross-user mutation tests executed.
- [ ] Live PostgreSQL rollback/concurrency/idempotency security gate executed.
- [ ] Audit immutability adversarial tests executed.
- [ ] Service-role / NO-BYPASSRLS production role verified.
- [ ] Production RLS activation decision.

## Phase 2 — Authorization / capability convergence
- [x] Canonical action vocabulary.
- [x] Fail-closed unknown action behavior.
- [x] Case ownership authorization.
- [x] Consent subject validation.
- [x] Consequential submission approval gate.
- [x] Submission idempotency boundary.
- [ ] Evidence mutation authorization fully mapped.
- [ ] Document read/edit authorization fully mapped.
- [ ] Child-row mutation authorization formally tied to parent capability.
- [ ] Delegation capability + action + resource semantics fully implemented.
- [ ] Delegation RLS only after end-to-end authorization convergence.
- [ ] Service identity authorization matrix finalized.

## Phase 3 — Runtime / deployment convergence
- [ ] Verify canonical API/Web runtime entrypoint.
- [ ] Verify worker/background process requirements.
- [ ] Verify Redis runtime path.
- [ ] Verify PostgreSQL runtime configuration.
- [ ] Verify storage/blob runtime path.
- [ ] Verify production environment-variable contract.
- [ ] Verify startup/readiness/health checks.
- [ ] Verify deployment configuration against canonical runtime.
- [ ] Consolidate competing CI workflows.
- [ ] Make CI the authoritative repeatable verification mechanism.
- [ ] Execute complete Python + Rust/Dioxus CI gate successfully.
- [ ] Add live PostgreSQL integration gate to authoritative CI.
- [ ] Add security/RLS gate to CI.

## Phase 4 — Shared infrastructure
### Identity
- [ ] Canonical identity contract across Web/Telegram/WhatsApp/Messenger/mobile.
- [ ] Session identity binding.
- [ ] Principal propagation across every adapter.
- [ ] Cross-surface identity correlation.
- [ ] Account recovery/identity lifecycle.

### Capability
- [x] Capability-oriented architecture.
- [x] Action Registry.
- [ ] Capability registry becomes complete ecosystem contract.
- [ ] Capability versioning.
- [ ] Capability compatibility policy.
- [ ] Capability observability.

### Consent / privacy
- [x] Explicit consent concepts.
- [x] Consent subject validation.
- [x] Atomic Consent + Case persistence boundary.
- [ ] Purpose-bound consent enforcement across every sensitive capability.
- [ ] Permission minimization / just-in-time access.
- [ ] Automatic capability/permission disablement after purpose completion where applicable.
- [ ] Re-activation requires renewed authorization/permission.
- [ ] Data retention/deletion policy implementation.
- [ ] DPDP/privacy operational controls.

### Storage
- [x] PostgreSQL provider-neutral direction.
- [x] Evidence/document persistence surfaces.
- [ ] Canonical object/blob storage abstraction.
- [ ] Backup/restore verification.
- [ ] Retention and deletion enforcement.
- [ ] Disaster recovery test.

### Audit / observability
- [x] Case audit schema.
- [ ] Immutable audit implementation proven under adversarial tests.
- [ ] Correlation IDs across surfaces.
- [ ] Security event telemetry.
- [ ] Operational metrics.
- [ ] Alerting/runbooks.

## Phase 5 — Independent ecosystem surfaces
- [ ] Web application production slice.
- [ ] Telegram adapter production slice.
- [ ] WhatsApp adapter.
- [ ] Messenger adapter.
- [ ] Android adapter.
- [ ] iOS adapter.
- [ ] DApp/Web3 adapter where justified.
- [ ] Telegram Mini App where justified.
- [ ] Shared capability consumption verified for each surface.
- [ ] Independent failure-domain tests.
- [ ] Shared policy/security contract tests.

## Phase 6 — Product capabilities
- [x] Civic Case domain foundation.
- [x] Evidence foundation.
- [x] Document generation/review foundation.
- [x] Submission foundation.
- [x] Consent foundation.
- [ ] Complete citizen-facing Web product.
- [ ] Citizen Intelligence Toolkit.
- [ ] Office/destination intelligence.
- [ ] Case tracking.
- [ ] Notification/reminder infrastructure.
- [ ] Feedback/accountability layer.
- [ ] AI/RAG capability as optional policy-controlled layer.
- [ ] Agentic AI capability with explicit user control and consequential-action gates.

## Phase 7 — Production readiness
- [ ] Security threat model refreshed against canonical architecture.
- [ ] Dependency/SBOM/security scanning.
- [ ] Secrets management.
- [ ] Backup/restore.
- [ ] Disaster recovery.
- [ ] Rate limiting/abuse controls.
- [ ] Privacy/data lifecycle controls.
- [ ] Incident response.
- [ ] Production observability.
- [ ] Load/performance testing.
- [ ] Failure injection / resilience testing.
- [ ] External integration verification.
- [ ] Release/rollback procedure.
- [ ] Production readiness review.

## Phase 8 — Ecosystem completion
A full-fledged ecosystem with fully shareable infrastructure is complete only when:
1. Independent surfaces consume the same capability contracts.
2. Identity, authorization, consent, policy, storage and audit are shared infrastructure.
3. No surface-specific implementation becomes the hidden source of truth.
4. PostgreSQL is a replaceable persistence implementation behind provider-neutral contracts, while remaining the relational production standard.
5. Security properties are proven at the database boundary.
6. Surfaces can fail independently.
7. Capabilities can evolve/version independently of surfaces.
8. New domain modules can reuse infrastructure without copying security/persistence code.
9. CI continuously proves these contracts.

## Completion estimate
- Repository architecture/convergence: ~80–85%
- Data/security foundation: ~65–70%
- Authorization convergence: ~65%
- Runtime/deployment: ~45–55%
- Shared infrastructure: ~45–55%
- Independent ecosystem surfaces: ~25–35%
- Product completeness: ~30–40%
- Production readiness: ~25–35%
- Full shared-infrastructure ecosystem: ~45–55%

These are engineering planning estimates, not measured project metrics. Repository evidence supports the completed items; percentages are synthesis based on remaining scope.

## Critical path
PostgreSQL live security gate → Authorization convergence → Runtime/deployment convergence → Shared identity + consent + policy + storage + audit → One production-quality Web vertical slice → Telegram/other adapters → Mobile/other surfaces → Ecosystem scale

## Current priority order
### P0
1. Live PostgreSQL security/RLS gate.
2. Evidence + Document mutation authorization.
3. Consent atomicity live verification.
4. Active Supabase/runtime dependency sweep.
5. Canonical CI convergence.

### P1
6. Runtime/deployment verification.
7. Shared identity contract.
8. Shared permission/consent lifecycle.
9. Canonical storage/blob abstraction.
10. Audit/observability hardening.

### P2
11. Production Web vertical slice.
12. Telegram/WhatsApp/Messenger adapters.
13. Citizen Intelligence Toolkit.
14. AI/RAG optional capability layer.
15. Mobile surfaces.

### P3
16. DApp/Web3/specialized surfaces where justified.
17. Ecosystem-scale resilience and performance.
18. Multi-domain reuse.

## Next 2 engineering steps
1. Execute the existing live PostgreSQL RLS/integration suites against the CI PostgreSQL service and fix every real failure rather than expanding the candidate policy prematurely.
2. Complete the active-code Supabase dependency sweep + CI/runtime convergence immediately after the database gate.

**Master rule:** archive historical implementations; never let archived architecture silently become an active dependency; never promote a candidate security policy based on static inspection alone.