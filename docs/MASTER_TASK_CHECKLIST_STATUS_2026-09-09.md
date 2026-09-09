# 🇮🇳 JANAVANI — MASTER TASK CHECKLIST STATUS REGISTER

**Date:** 9 September 2026  
**Purpose:** Reconcile the canonical Master Task Checklist against the latest Janavani architecture, repository-audit evidence, and project decisions.  
**Authority:** `docs/MASTER_TASK_CHECKLIST.md` remains the canonical task inventory. This dated register updates execution priority/status; it does not replace the canonical checklist.

## 1. EXECUTIVE AUDIT

Janavani is architecturally strong but implementation is still materially behind the full ecosystem scope. The current priority is **convergence + verification + one complete civic-action vertical slice**, not creation of additional architectural generations.

Engineering planning estimate remains approximately **25–30% production-grade ecosystem readiness**. This is an engineering estimate, not a repository claim.

The 9 September verification pass confirms that the repository has moved further toward convergence: duplicate civic-action/case-flow material has been archived, the canonical civic-action capability is now the active composition boundary, the canonical Docker entry point has been aligned with the canonical FastAPI assembly, and the latest relevant CI evidence remains successful for Architecture Guard and Security CI. Full runtime/test-suite evidence is still incomplete.

## 2. HARD ARCHITECTURAL INVARIANTS — LOCKED

- [x] Janavani is the **complete ecosystem**, not an MVP-only product boundary.
- [x] Shared infrastructure first; interfaces are consumers, not owners of business logic.
- [x] One canonical Case and civic-action lifecycle across surfaces.
- [x] Web, Android, iOS, Telegram Bot, Telegram Mini App, WhatsApp, Messenger and DApp are independent access surfaces.
- [x] Capability exists in the ecosystem even when a user chooses not to invoke it.
- [x] **Optional means user choice, not ecosystem omission.**
- [x] AI is a core shared capability; AI invocation is user-controlled.
- [x] Agentic AI is a shared capability; tools and consequential actions remain policy/consent controlled.
- [x] Privacy/safety are cross-cutting controls, not channel-specific features.
- [x] Personal/sensitive data remains under user/device control by default; no unnecessary central collection.
- [x] Evidence originals remain local unless an explicitly authorised operation requires transmission.
- [x] Document generation is separate from submission; generated documents are for user review/correction/print/download.
- [x] Provider neutrality: PostgreSQL, Ollama, cloud AI, Freenet, Nostr, Web3, storage and future providers are adapters, not domain authorities.
- [x] Rust is the canonical long-term domain/core direction; Python remains useful at application/integration edges during migration.
- [x] Mojo is research/watchlist only; it is not a current canonical Janavani language.
- [x] Archive first; delete only after dependency, replacement, runtime and historical-value evidence.
- [x] Never claim implementation completion from design/code alone; require tests, runtime and evidence.

## 3. REPRIORITIZED EXECUTION FRONTIER

### P0-A — SOURCE OF TRUTH / GOVERNANCE

- [ ] Reconcile North Star, Ecosystem Charter, Source of Truth, Master Architecture, Product Landscape, Roadmap, Capability Registry and Master Checklist terminology.
- [ ] Establish one current execution frontier and prevent duplicate task generations.
- [ ] Create/maintain ADR decision index for major architecture decisions.
- [x] Add explicit capability → repository → tests → CI/deployment evidence mapping.

### P0-B — GITHUB / REPOSITORY CONVERGENCE

- [ ] Establish current `main` runtime truth across Render/Vercel/Docker/local entry points.
- [x] Verify canonical API/service execution paths in repository configuration.
- [x] Verify Case storage ownership and provider boundaries at repository level.
- [ ] Verify current AI/provider integrations.
- [ ] Verify SOS runtime claims before marking implementation complete.
- [ ] Audit branches/PRs for useful work; preserve before consolidation.
- [ ] Consolidate duplicate generations of lifecycle, consent, WebApp, storage, architecture guards and provider adapters.
- [ ] Archive superseded work with evidence; delete only after archive-readiness checks.
- [x] Latest `main` Architecture Guard run succeeded on commit `73256de29482891b0a708a39d49374a8e4b80306`.
- [x] Latest `main` Security CI run succeeded on commit `73256de29482891b0a708a39d49374a8e4b80306`.
- [ ] Record full Python/Rust/Dioxus test execution evidence for the current `main` commit.

### P0-C — CANONICAL CORE

- [x] Rust canonical Case/lifecycle direction established.
- [x] Cross-language lifecycle/serialization convergence work established.
- [ ] Complete canonical Identity/Actor model.
- [ ] Complete canonical Consent/Permission model and runtime enforcement.
- [ ] Complete canonical Evidence + Provenance model.
- [ ] Complete canonical Authority/Jurisdiction model.
- [ ] Complete canonical Document model.
- [ ] Complete canonical Submission/Delivery/Tracking model.
- [ ] Complete canonical Policy/Audit model.
- [ ] Define stable application/service contracts around the core.

### P0-D — PRIVACY / TRUST / STORAGE

- [x] Local-first privacy architecture established.
- [x] Device-key boundary established.
- [x] User-controlled recovery architecture established at design/prototype level.
- [x] Data classification/policy and agent-tool policy direction established.
- [ ] Verify actual Web Crypto + IndexedDB implementation end-to-end.
- [ ] Complete key recovery/migration threat model and security review.
- [ ] Complete local evidence storage with original preservation.
- [ ] Implement EXIF/GPS metadata minimisation and explicit location modes.
- [ ] Complete encryption/key lifecycle tests.
- [ ] Complete DPDP/privacy-policy conformance evidence.

### P0-E — FLAGSHIP CIVIC-ACTION VERTICAL SLICE

**Target:** one complete, deterministic, reusable civic journey before broad interface expansion.

- [x] Canonical Case creation capability exists with identity/authorization boundary.
- [x] Canonical civic-action composition boundary exists and is used by the current Web civic-case adapter.
- [ ] Create Case — complete end-to-end persistence/runtime evidence.
- [ ] Understand/structure citizen issue.
- [ ] Determine jurisdiction.
- [ ] Resolve responsible authority from verified sources.
- [ ] Collect/register local evidence.
- [ ] Preserve provenance/integrity metadata.
- [ ] Select civic action type.
- [x] Generate reviewable document draft through canonical civic-action capability.
- [ ] Allow user editing/correction.
- [ ] User explicitly approves final document.
- [x] PDF + DOCX renderer contract has focused coverage.
- [ ] Generate PDF — end-to-end runtime evidence.
- [ ] Generate editable document — end-to-end runtime evidence.
- [ ] Provide print/download/submission instructions.
- [x] Submission is represented as a separate explicit Case lifecycle capability; external delivery is not implicit.
- [ ] Record acknowledgement/tracking when a submission mechanism exists.

### P0-F — WEBAPP REFERENCE CLIENT

- [x] Canonical FastAPI assembly boundary exists at `src/web/canonical_app.py`.
- [x] Web civic-case HTTP adapter consumes shared Case/CivicAction capabilities and authenticated identity dependency.
- [ ] Canonical WebApp shell consumes shared contracts only.
- [ ] Case workspace.
- [ ] Evidence workspace.
- [ ] Authority workspace.
- [ ] Document review/editor.
- [ ] Consent/privacy controls.
- [ ] Timeline/provenance view.
- [ ] PDF/DOCX output.
- [ ] Runtime/E2E verification.

### P1-A — TELEGRAM CONVERGENCE

- [x] Telegram conversation foundation exists.
- [x] Telegram composition imports shared case/civic-action repository/capability factories.
- [ ] Migrate remaining Telegram business logic to shared capability contracts.
- [ ] Complete capability parity matrix against the canonical ecosystem inventory.
- [ ] Preserve Telegram failure isolation.
- [ ] Establish Bot ↔ Mini App continuity without accidental identity linking.
- [ ] Verify Telegram can consume the same Case lifecycle as WebApp.

### P1-B — AI / AGENTIC AI

- [x] Provider-neutral AI boundary established.
- [x] Agent tool-policy direction established.
- [ ] Production AI provider abstraction.
- [ ] Local AI/Ollama provider evaluation and runtime verification.
- [ ] RAG with authoritative citations/freshness.
- [ ] AI data-boundary enforcement.
- [ ] User AI/no-AI choice at capability invocation.
- [ ] Agent confirmation gates.
- [ ] AI safety/evaluation/hallucination reporting.
- [ ] AI/agent provenance.

### P1-C — AUTHORITY / GOVERNMENT INFORMATION

- [ ] Authority directory.
- [ ] Jurisdiction database.
- [ ] Office directory.
- [ ] Official-source verification.
- [ ] Freshness monitoring.
- [ ] Responsible-authority resolution.
- [ ] Action-path recommendation.
- [ ] Recipient/CC verification.

### P1-D — DOCUMENT / EVIDENCE

- [ ] Canonical template library.
- [ ] Complaint/grievance/RTI/petition/representation templates.
- [ ] To + CC address handling.
- [ ] User correction workflow.
- [ ] Source/expert verification.
- [ ] Evidence passport/provenance model.
- [ ] Scanned-document OCR with original preservation.
- [ ] Indian-language OCR evaluation.

### P2 — EXPANSION AFTER FLAGSHIP SLICE

- [ ] Telegram Mini App.
- [ ] Android.
- [ ] iOS.
- [ ] WhatsApp.
- [ ] Messenger.
- [ ] DApp/Web3.
- [ ] Offline/local-first expansion.
- [ ] SOS production implementation.
- [ ] Mesh/Reticulum/LoRa/Meshtastic assessment and implementation.
- [ ] Satellite capability assessment/implementation.
- [ ] Decentralized storage/verification providers.
- [ ] Government schemes/benefits intelligence.
- [ ] Accountability/knowledge contribution ecosystem.
- [ ] Whistleblower system.
- [ ] Financial transparency/contribution system.

## 4. TASKS THAT MUST NOT BE TREATED AS ACTIVE ENGINEERING FRONTIER YET

These remain valid ecosystem scope, but should not compete with P0/P1 execution:

- Advanced blockchain/Web3 expansion beyond required provider contracts.
- Freenet production integration before provider contract + readiness evidence.
- Mesh/satellite field deployment before SOS core verification.
- Android/iOS parallel implementation before shared contracts and flagship Web slice stabilise.
- Large AI/agent platform expansion before deterministic civic workflow is complete.
- Mojo adoption before a measured hardware/performance requirement justifies it.

## 5. CURRENT MASTER PRIORITY ORDER

```text
P0  Source of Truth / Governance
 ↓
P0  GitHub + runtime + storage convergence
 ↓
P0  Canonical Rust/domain/application contracts
 ↓
P0  Identity + consent + privacy/trust enforcement
 ↓
P0  Case + Evidence + Provenance + Authority + Document
 ↓
P0  Complete civic-action vertical slice
 ↓
P0  WebApp reference client
 ↓
P1  Telegram Bot convergence
 ↓
P1  Telegram Mini App
 ↓
P1  AI / Agentic AI production integration
 ↓
P1  Cross-surface continuity/parity
 ↓
P2  Android / iOS
 ↓
P2  WhatsApp / Messenger
 ↓
P2  DApp/Web3 + decentralized providers
 ↓
P2  Offline / mesh / satellite expansion
 ↓
FULL JANAVANI ECOSYSTEM
```

## 6. NEXT 10 CONCRETE TASKS

1. M2-B Capability → Repository → Test → Deployment mapping — **initial verified map complete**.
2. M2-C Storage ownership decision/verification — **partially verified; provider boundaries are clear, production activation remains gated**.
3. M2-D Runtime execution verification — **repository entry-point alignment verified; live deployment evidence remains open**.
4. Consolidate remaining duplicate architecture/storage generations using archive-first evidence.
5. Complete canonical Identity + Consent runtime contracts and trusted HTTP/API binding.
6. Complete local Evidence + Provenance implementation and verification.
7. Implement Authority/Jurisdiction provider with source freshness/provenance.
8. Implement canonical Document/template engine with PDF + editable output and user correction.
9. Connect Case → Evidence → Authority → Document → Review into one tested vertical slice.
10. Build/verify the WebApp reference client against shared contracts, then complete Telegram convergence.

## 7. CURRENT VERIFICATION EVIDENCE — 2026-09-09

### Repository state

- Current default branch: `main`.
- Latest documentation/status commit before this verification: `73256de29482891b0a708a39d49374a8e4b80306`.
- M2-B map commit: `1c79dbe01766367c96b86eed94a9009c90d218ae`.
- Docker runtime alignment commit: `764ab0c36560378b7274a5747d2e5854eacc772e`.
- M2-C/M2-D verification record: `ffebfee9d6fc51130bca65db9b3e2498edafda4a`.
- The latest preceding convergence merge is `faacf77101bad25672e2e3976116cae8280ddfd5` (PR #102), which archived the duplicate civic-action helper and migrated renderer coverage to the canonical civic-action capability.
- The preceding case-flow convergence merge is `8466398c20b6568f1edc8a01ddda30359a43eb` (PR #101).

### Confirmed active implementation boundaries

- `src/capabilities/civic_case.py` is the provider/surface-neutral Case command/query boundary and performs authorization before persistence.
- `src/web/civic_case_router.py` is an HTTP adapter and obtains identity through `require_authenticated_identity`; it does not accept `created_by` as trusted authentication.
- `src/web/canonical_app.py` is the canonical FastAPI assembly boundary.
- `src/storage/repositories/provider.py` selects `memory`, `postgres`, or `supabase` behind `CivicCaseRepository` rather than letting surfaces choose database implementations.
- `src/storage/repositories/postgres_civic_case.py` is the current strongest durable Case adapter and uses the shared PostgreSQL Unit-of-Work boundary.
- `src/storage/repositories/supabase_civic_case.py` remains an adapter but is not production-transaction-authoritative because multi-table atomicity is explicitly not claimed.
- The capability registry identifies CASE, AUTHORITY, DOCUMENT, IDENTITY, CONSENT, EVIDENCE, SEARCH, AI, NOTIFICATION and AUDIT as shared capabilities.

### Runtime/deployment verification

- `render.yaml` points directly to `src.web.canonical_app:app`.
- `entrypoint.sh` points directly to `src.web.canonical_app:app`.
- `Dockerfile` was aligned in this pass to point directly to `src.web.canonical_app:app`; it no longer uses the compatibility `src.web.app:app` hop.
- `src/web/app.py` remains a deliberately thin compatibility entry point and delegates to the canonical assembly.
- `docker-compose.yml` remains a broader local ecosystem configuration and is **not** treated as verified production topology.
- Live Render/Vercel HTTP evidence and actual deployed environment/provider values remain open.

### Storage verification

- The canonical schema contract explicitly separates Case metadata from evidence/document binary artifacts.
- PostgreSQL stores Case metadata and references; object storage owns binary artifacts.
- Consent remains independently owned and is not synthetically manufactured by Case persistence.
- `POSTGRESQL_MIGRATION_DRAFT.sql` is explicitly review-only and not authorized for production execution.

### CI evidence

- Architecture Guard for `73256de29482891b0a708a39d49374a8e4b80306`: **SUCCESS**.
- Security CI for the same commit: **SUCCESS**.
- Architecture Guard job completed successfully and executed deterministic architecture guard, cross-language architecture conformance, archive safety evidence, and serialization schema conformance.
- Full Python/Rust/Dioxus `run_all_tests.sh` execution has **not** been independently verified in this review. The repository's orchestrator requires Python tests plus Rust core/application/client suites, so configuration existence is not treated as passing evidence.
- Local clone/test execution was previously attempted in the available environment but external GitHub DNS/network access was unavailable; therefore no local test result is claimed.

### Runtime/storage finding

The repository deliberately defaults the Case repository to `memory` outside production. Production configuration fails closed unless durable Case/artifact/evidence providers and required storage settings are supplied. Therefore **Render/free-tier development should not be confused with production persistence readiness**.

The production contract documents `JANAVANI_RUNTIME_MODE=production`, `JANAVANI_CASE_REPOSITORY_PROVIDER=postgres`, `JANAVANI_ARTIFACT_REPOSITORY_PROVIDER=postgres`, `JANAVANI_EVIDENCE_REPOSITORY_PROVIDER=postgres`, `JANAVANI_ARTIFACT_BLOB_PROVIDER=s3`, `JANAVANI_POSTGRES_DSN`, and the artifact bucket as production requirements. These remain deployment-time configuration items, not something to force prematurely while the product slice is still under construction.

## 8. STATUS INTERPRETATION

Use these states strictly:

- **COMPLETE:** implementation + tests + repository verification + required security/privacy review + functional/runtime evidence.
- **VERIFYING:** implementation exists but required evidence is incomplete.
- **DESIGN COMPLETE:** contract/architecture exists; implementation is not implied.
- **IN PROGRESS:** active implementation/convergence.
- **NOT STARTED:** no verified implementation.
- **BLOCKED:** dependency prevents execution.
- **ARCHIVED:** superseded material preserved with reason/evidence.

## 9. CHANGE LOG

| Date | Change |
|---|---|
| 2026-09-09 | Reconciled latest Janavani architecture/project history with canonical Master Task Checklist. |
| 2026-09-09 | Shifted execution frontier from architecture invention to convergence, verification and flagship civic-action vertical slice. |
| 2026-09-09 | Reaffirmed complete-ecosystem scope and user-choice interpretation of “optional”. |
| 2026-09-09 | Reaffirmed shared-infrastructure-first, one-Case, provider-neutral, privacy-first architecture. |
| 2026-09-09 | Deferred broad channel/AI/Web3/hardware expansion until core vertical slice dependencies are verified. |
| 2026-09-09 | Verified successful Architecture Guard + Security CI runs on latest convergence/status commit. |
| 2026-09-09 | Recorded current canonical Case/CivicAction/Web adapter/storage provider boundaries and test-evidence limitation. |
| 2026-09-09 | Verified M2-C storage ownership boundaries and M2-D repository-declared runtime entry points. |
| 2026-09-09 | Corrected Dockerfile to invoke the canonical FastAPI assembly directly. |
| 2026-09-09 | Recorded M2-C/M2-D verification evidence; live deployment and full-suite execution remain open. |

**Master rule:** Preserve the full ecosystem scope, but execute only the highest-value unresolved dependency frontier. Never mark design as implementation. Never delete history before evidence-backed archival.