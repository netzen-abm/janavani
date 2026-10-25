# 🇮🇳 JANAVANI — MASTER TASK CHECKLIST

**Status:** LIVE MASTER CONTROL DOCUMENT  
**Version:** 1.4  
**Date:** 25 October 2026  
**Scope:** COMPLETE JANAVANI ECOSYSTEM — NOT AN MVP

**Purpose:** Single authoritative checklist for tracking the complete Janavani ecosystem. It records master workstreams, subtasks, dependencies, verification status, and completion evidence.

> **Canonical scope rule:** Janavani is being built as a complete citizen-governance ecosystem. Web, Android, iOS, Telegram Bot, Telegram Mini App, WhatsApp, Messenger, DApp/Web3, AI/non-AI paths, resilient mesh and satellite capabilities are ecosystem surfaces/capabilities. Individual milestones are construction stages, not the product boundary.

> **Completion rule:** A task is not COMPLETE merely because code or documentation exists. Engineering completion requires implementation, tests, repository verification, security/privacy review where applicable, functional verification, and evidence. Design completion is explicitly labelled DESIGN COMPLETE and must not be confused with implementation completion.

## 0A. EXECUTIVE REBASELINE — 08 OCTOBER 2026

**Decision:** Convergence before expansion. The ecosystem scope remains unchanged; the immediate objective is to make one canonical civic-action system correct, durable, testable and reusable across independent surfaces.

### P0 — Canonical correctness / release blockers
1. **Case/content → lifecycle → submission cascade** — resolve remaining failures, then rerun the canonical suite.
2. **Runtime truth** — verify canonical Web/API entry point, Telegram runtime, restart/recovery behavior and deployment startup.
3. **PostgreSQL/RLS** — prove cross-user isolation, provider contract behavior, migration/rollback, backup/restore and failure recovery.
4. **Security/privacy** — verify authorization, consent, data minimization, session expiry, logging redaction and device/local-data boundaries.

### P1 — Independent failure isolation
After P0 is green, isolate and fix only genuinely independent failures:
- identity/authentication/authorization;
- PostgreSQL/RLS/provider runtime;
- AI provider/routing;
- session expiry/recovery;
- Rust/Python/domain parity.

These must not be coupled into a new universal orchestration layer.

### P2 — Shared capability convergence
- Case, Evidence, Authority, Document, Consent, Submission and Tracking remain canonical shared capabilities.
- Surface adapters consume capabilities; they do not reimplement them.
- Split code only at boundaries of change, trust, persistence, provider dependency or independent reuse.
- Keep tightly coupled invariants together.

### P3 — First complete civic-action vertical slice
**Issue → Case → Authority → Evidence → Document → Review → Consent → Submission → Acknowledgement → Tracking → Follow-up/Outcome.**

The Dynamic Web is the first proving surface, while Telegram remains independently operable. Neither becomes the platform core.

### P4 — Ecosystem expansion
Only after the canonical slice is green: Mini App, WhatsApp/Messenger, Android/iOS, AI/RAG/Agentic expansion, DApp/Web3, resilience/mesh/satellite and advanced governance capabilities.

### P5 — Repository hygiene
- Exactly **nine active branches**; the live repository currently satisfies this.
- No blind merge or deletion of historical work.
- Preserve useful work, selectively extract unique changes, verify, then retire/archive references.
- Do not create another architecture generation merely to solve an existing convergence problem.

### Explicit next two steps
1. **Resolve the remaining Case/content → lifecycle → submission cascade and rerun the canonical suite.**
2. **Once that cascade is green, isolate the genuinely independent failures—identity, PostgreSQL/RLS, AI provider, session expiry and Rust parity—without introducing architectural coupling.**

### Branch policy
The nine approved active branches are: main, integration/canonical-platform, feat/canonical-case-kernel, feat/canonical-capability-execution-envelope, feat/canonical-civic-action-vertical-slice, feat/canonical-sos-contract, feat/capability-scoped-consent-agent-enforcement, audit/postgres-provider-production-gates, chore/ecosystem-shared-capability-infrastructure.

### Evidence baseline from live GitHub audit
- Exactly 9 branches observed.
- feat/canonical-capability-execution-envelope and chore/ecosystem-shared-capability-infrastructure are 0 commits ahead of main; they do not need merging.
- integration/canonical-platform contains unique work but is deeply behind main; do not wholesale-merge.
- Case-kernel, civic-action and SOS branches contain historical/divergent work; selectively extract only missing, still-valid changes.
- Consent/agent and PostgreSQL-gate branches contain unique work but are based on old generations; re-evaluate against current contracts before integration.
- PR #203 remains a convergence review vehicle and is not merge-ready merely because it is mergeable.



### Verified follow-up on the rebaseline commit — 11 October 2026

- [x] Latest observed review-head checks for `f29feb8076b8043269a71cc47fa06afecc98252c`: CI, Docker, Architecture Guard, Security CI and Dependency Review all completed successfully.
- [x] Telegram pairing command is registered by `src/bot_telegram.py`; its service is only composed when the `external_identity_links` provider is PostgreSQL. This verifies source wiring, not that a live Telegram Worker exists.
- [ ] Fresh default CodeQL analysis must be confirmed on the current review head; custom Security CI success is not sufficient.
- [ ] Current live Render service inventory still contains only the Web/API service. The `render.yaml` worker definition is not proof that the Telegram Worker has been created.
- [ ] Do not promote the browser `/app` local-draft workspace as the full WebApp. Case persistence, evidence lifecycle, authenticated cross-surface continuation, submission, acknowledgement and tracking are not yet jointly verified in the deployed system.

## 0B. LIVE REBASELINE — 11 OCTOBER 2026

**Status:** ACTIVE REBASELINE — supersedes older checklist statements about the current physical branch count and current PR security workflow; dated material remains as historical evidence.

**Audit record:** [2026-10-11 live rebaseline and code audit](90-audits/2026-10-11-live-rebaseline-and-code-audit.md)

### Live baseline

- [x] Canonical `main` SHA recorded: `0fb4c50d188811bed700555e1ed82735adef790e`.
- [x] Main-tree source inventory: 1,048 tree entries; 292 active `.py/.rs` files under `src/`, `api/`, and `crates/` after archive/historical exclusions.
- [x] CI has an active-source line guard at 180 lines.
- [x] Latest observed PR #204 head `6ff2f2788ead52ee08943b97887f83f2d913a796` passed the canonical CI test job, including the line guard, smoke, Web vertical-slice, Web/Telegram shared capability, full canonical suite, live PostgreSQL RLS, identity-pairing, backup/restore and restart-durability gates.
- [x] Docker, Architecture Guard, Security CI and Dependency Review were green for that observed PR head.
- [x] Advanced CodeQL job was tested and failed because GitHub default CodeQL setup is enabled (`CodeQL analyses from advanced configurations cannot be processed when the default setup is enabled`, run `38123086974`). The duplicate advanced job was removed again in `b04a2c538f0936d26b6f7ba3d70742a1d41a53f0`.
- [ ] Re-run and inspect fresh custom security/CI checks after de-duplicating CodeQL; separately verify that default CodeQL analysis is actively completing and current.
- [ ] The live repository currently has **10 physical branches**, not nine, because an extra `audit/2026-10-11-live-rebaseline` branch was accidentally created during the audit. The exact-nine invariant is therefore BLOCKED until that extra ref is archived/deleted and GitHub verifies nine refs.
- [ ] Deployed Web/API liveness and independent Telegram runtime evidence remain unverified. Live Render inventory showed only the Web/API service; no Telegram Worker was configured in the connected workspace.

### Pull-request disposition

- **PR #203:** open/unmerged; convergence review vehicle, not a wholesale merge candidate. Compare selectively against current main.
- **PR #204:** keep draft until fresh CI passes, default CodeQL is verified as actively analyzing (do not combine with the conflicting advanced job), and the trusted identity gateway, dedicated least-privilege shared database role, independent protected-data authorization and deployment/runtime gates are reviewed.
- PR #204 adds a local draft / preview / download / print workspace at `/app`. That route is not present in the currently deployed `main` revision; merge/deploy and runtime verification are required before advertising it. Even after deployment, it is not the complete persisted Case, submission and tracking experience.

### Exact branch-recovery action

Use the existing [Branch Retirement workflow](https://github.com/netzen-abm/janavani/actions/workflows/branch-retirement.yml) on `main`, with `execute=true` and confirmation exactly `RETIRE-LEGACY-BRANCHES`. The workflow is designed to archive each non-approved head as a tag before deleting its physical branch ref, then assert that nine refs remain. Review its logs and re-query branches afterwards. The connected GitHub action surface does not offer workflow dispatch or branch-ref deletion, so this session could not execute that operation. Do not claim the nine-branch rule is satisfied until the physical count is verified.

### Current priority order

**P0 — repository and runtime truth**
1. Retire only the accidental extra audit branch through the guarded workflow; re-verify exactly nine branches.
2. Verify fresh Security CI/CI outcomes and confirm GitHub's default CodeQL setup is producing current analyses; do not re-enable the conflicting advanced job.
3. Verify canonical Web/API and Telegram startup, health, provider configuration and mutual failure independence in the actual deployment.
4. Re-check PostgreSQL RLS/cross-user denials, least-privilege roles, atomicity/rollback, migration behavior, restart/outage recovery and backup/restore against deployment-equivalent configuration.

**P1 — the first complete citizen workflow**
5. Complete and verify `issue → Case → authority → evidence reference → document → review/correction → explicit consent → submission preparation → acknowledgement/tracking → follow-up/outcome` on Web.
6. Provide the corresponding Telegram workflow through the same shared capability graph. Telegram remains independently deployed and must not own a duplicate civic domain.
7. Verify cross-surface Case continuation only once shared identity, authorization and durable persistence are proven together. Keep personal/sensitive content and evidence device-first by default; document generation is not submission, and delivery attempts are not acknowledgements.

**P2 — defect-driven convergence**
8. Fix the smallest reproducible boundary-local defect. Do not add a generic orchestrator or split cohesive code for line-count cosmetics.
9. Re-run focused tests, canonical suite and security/runtime gates after each meaningful change; record SHA and direct evidence.

**P3 — expansion**
10. Expand Mini App, WhatsApp/Messenger, Android/iOS, AI/RAG/Agentic AI, DApp/Web3 and resilient transports only after the proving gates pass. The ecosystem scope remains complete; this is sequencing, not scope reduction.

### Code-responsibility rule reaffirmed

Split only at independent boundaries of change ownership, trust/security, persistence, provider dependency, reuse, lifecycle/state testing, or external transport. Preserve cohesive invariants. The 180-line CI rule is a guard, not permission to fragment responsibilities arbitrarily.

### Next 2 steps

1. **Remove the accidental extra branch through the archive-first Branch Retirement workflow, then verify nine refs and fresh CI/default-CodeQL evidence.**
2. **Apply and verify `/liveness` on the Render Web/API service; configure the Telegram bot as an independent Worker; then finish the same end-to-end civic-action journey across both surfaces** using shared capabilities and explicit consent/persistence controls.

---

---

# 0. CHECKLIST GOVERNANCE

- [x] 0.1 Keep this file in GitHub as the canonical master checklist.
- [x] 0.2 Every major capability/workstream has a master task ID.
- [x] 0.3 Every master task contains explicit subtasks.
- [x] 0.4 Use status vocabulary: `NOT STARTED / IN PROGRESS / BLOCKED / VERIFYING / DESIGN COMPLETE / COMPLETE / ARCHIVED`.
- [x] 0.5 Record evidence for completed work in dated status/audit documents.
- [x] 0.6 Verify actual repository files before claiming completion.
- [x] 0.7 Never silently remove completed or obsolete work; archive only after verification.
- [x] 0.8 Reconcile this checklist whenever architecture or verified evidence changes.
- [x] 0.9 Before starting a new audit, inspect the latest checklist, status register and relevant dated audits; audit only the unresolved delta.

---

# 1. MASTER ARCHITECTURE & SYSTEM GOVERNANCE

**Status: IN PROGRESS — DESIGN FOUNDATION SUBSTANTIALLY DEFINED**

- [x] 1.1 Create `docs/JANAVANI_MASTER_ARCHITECTURE.md`.
- [x] 1.2 Lock capability-first architecture.
- [x] 1.3 Lock independent channel principle.
- [x] 1.4 Lock AI/non-AI independence principle.
- [x] 1.5 Lock mesh as current SOS capability.
- [x] 1.6 Lock satellite as current SOS capability.
- [x] 1.7 Lock archive-over-delete principle.
- [x] 1.8 Create capability registry — DESIGN COMPLETE: `docs/CAPABILITY_REGISTRY.md`.
- [x] 1.9 Create core data contracts — DESIGN COMPLETE: `docs/DATA_CONTRACTS.md`.
- [x] 1.10 Create permission/consent contracts — APPLICATION SESSION LIFECYCLE IMPLEMENTED; platform-adapter verification remains open.
- [ ] 1.11 Create transport abstraction contracts.
- [ ] 1.12 Create failure/dependency matrix.
- [ ] 1.13 Create system-wide threat model.
- [ ] 1.14 Create system-wide test strategy.

---

# 2. REPOSITORY BASELINE & ARCHITECTURE RECONCILIATION

**Status: IN PROGRESS — STATIC MAPPING SUBSTANTIALLY COMPLETE; RUNTIME VERIFICATION OPEN**

- [x] 2.1 Static repository/tree inventory.
- [ ] 2.2 Live runtime entry-point verification.
- [ ] 2.3 Runtime API/service execution inventory.
- [x] 2.4 Static database/storage inventory.
- [ ] 2.5 Runtime AI integration verification.
- [x] 2.6 Static decentralized-component inventory.
- [ ] 2.7 Runtime SOS execution verification.
- [ ] 2.8 Test/CI execution evidence inventory.
- [x] 2.9 Static implementation-vs-architecture comparison.
- [x] 2.10 Preliminary static duplicate/obsolete identification.
- [ ] 2.11 Archive obsolete material only after dependency/replacement/runtime verification.
- [x] 2.12 Static architecture-gap report.

Evidence: `docs/REPOSITORY_RECONCILIATION_AUDIT_2026-08-23.md`, `docs/RUNTIME_IMPORT_DEPENDENCY_MAP_2026-08-23.md`, `docs/DEPLOYMENT_TOPOLOGY_AUDIT_2026-08-23.md` and dated status register.

---

# 3. CAPABILITY REGISTRY

**Status: DESIGN COMPLETE — IMPLEMENTATION MAPPING PENDING**

- [x] 3.1 Define capability ID convention.
- [x] 3.2 Define capability metadata schema.
- [x] 3.3 Define permission requirements.
- [x] 3.4 Define identity requirements.
- [x] 3.5 Define AI dependency flag.
- [x] 3.6 Define offline/local support flag.
- [x] 3.7 Define channel support.
- [x] 3.8 Define transport support.
- [x] 3.9 Define fallback behavior.
- [x] 3.10 Register civic-document capabilities.
- [x] 3.11 Register government-information capabilities.
- [x] 3.12 Register accountability capabilities.
- [x] 3.13 Register evidence capabilities.
- [x] 3.14 Register expert/volunteer capabilities.
- [x] 3.15 Register SOS capabilities.
- [x] 3.16 Register financial-transparency capabilities.

Remaining: capability → repository → tests → deployment → security/privacy evidence mapping.

---

# 4. CORE DATA CONTRACTS

**Status: DESIGN COMPLETE — IMPLEMENTATION/STORAGE MAPPING PENDING**

- [x] 4.1 Identity contract.
- [x] 4.2 Consent contract.
- [x] 4.3 User preference contract.
- [x] 4.4 Case/complaint contract.
- [x] 4.5 Government office contract.
- [x] 4.6 Officer/public-servant contract.
- [x] 4.7 Political representative contract.
- [x] 4.8 Scheme/benefit contract.
- [x] 4.9 Document contract.
- [x] 4.10 Address/contact contract.
- [x] 4.11 Evidence contract.
- [x] 4.12 Source/provenance contract.
- [x] 4.13 Expert review contract.
- [x] 4.14 Correction/submission contract.
- [x] 4.15 SOS packet contract.
- [x] 4.16 Government alert contract.
- [x] 4.17 Financial transaction/disclosure contract.
- [x] 4.18 Archive/retention contract.

**Control:** No database migration, destructive storage change or schema replacement is authorised solely because a contract exists.

---

# 5. IDENTITY, ACCESS & USER CONTROL

**Status: IN PROGRESS — FOUNDATION EXISTS; RUNTIME/CHANNEL VERIFICATION OPEN**

- [ ] 5.1 Optional account model.
- [ ] 5.2 Channel-specific authentication.
- [ ] 5.3 Cross-channel identity linking only with consent.
- [ ] 5.4 Role/permission system.
- [ ] 5.5 Expert permissions.
- [ ] 5.6 Volunteer permissions.
- [ ] 5.7 NGO/institution permissions.
- [ ] 5.8 Government-source verification permissions.
- [ ] 5.9 Revocation mechanism.
- [ ] 5.10 Access audit log.

# 6. MULTILINGUAL & ACCESSIBILITY

**Status: NOT STARTED**

- [ ] 6.1 English default interface language.
- [ ] 6.2 Indian-language architecture.
- [ ] 6.3 Language detection without overriding user preference.
- [ ] 6.4 Translation quality workflow.
- [ ] 6.5 Official-source vs translated/generated distinction.
- [ ] 6.6 Accessibility baseline.
- [ ] 6.7 Voice input/output where supported.
- [ ] 6.8 Low-bandwidth UX.
- [ ] 6.9 Offline UX.

# 7. OCR, COMPUTER VISION & DOCUMENT UNDERSTANDING

**Status: NOT STARTED**

- [ ] 7.1 OCR pipeline.
- [ ] 7.2 Indian-script OCR evaluation.
- [ ] 7.3 Document classification.
- [ ] 7.4 Table/form extraction.
- [ ] 7.5 Image understanding.
- [ ] 7.6 Evidence quality checks.
- [ ] 7.7 Human correction workflow.
- [ ] 7.8 Source provenance preservation.
- [ ] 7.9 Offline/local OCR where feasible.

# 8. RAG / SLM / LLM / AGENTIC AI

**Status: IN PROGRESS — SHARED AI CONTRACT/GATEWAY IMPLEMENTED; PROVIDER CONVERGENCE + RUNTIME VERIFICATION OPEN**

- [x] 8.1 AI provider abstraction — `src/ai/provider.py`.
- [x] 8.2 Local/SLM capability assessment and canonical Ollama provider conformance.
- [ ] 8.3 RAG architecture.
- [ ] 8.4 Source citation requirements.
- [ ] 8.5 Knowledge freshness policy.
- [ ] 8.6 LLM routing policy.
- [x] 8.7 Agentic AI tool permissions — shared policy/gateway foundation exists.
- [x] 8.8 Human approval gates — consequential-operation boundary exists.
- [x] 8.9 AI failure fallback — deterministic/degraded path exists for current drafting flow.
- [ ] 8.10 AI safety/evaluation suite.
- [ ] 8.11 Prompt/version registry.
- [ ] 8.12 Hallucination/error reporting.

**Immediate AI convergence finding:** concrete AI providers are now confined to `src/ai/composition.py` and provider adapters. `TranslationCapability` and `JanavaniLegalAgent` consume the provider-neutral `AIProvider` contract and canonical `AIExecutionGateway`; remaining AI work is provider registration/routing and verification evidence, not provider leakage into capabilities.

# 9. CIVIC DOCUMENT & LETTER ENGINE

**Status: IN PROGRESS — ARCHITECTURE + PARTIAL IMPLEMENTATION; VERTICAL-SLICE VERIFICATION PRIORITY**

- [ ] 9.1 Complaint drafting.
- [ ] 9.2 Grievance drafting.
- [ ] 9.3 RTI drafting.
- [ ] 9.4 Petition drafting.
- [ ] 9.5 Representation drafting.
- [ ] 9.6 Objection drafting.
- [ ] 9.7 Appeal/follow-up drafting.
- [ ] 9.8 Escalation-letter drafting.
- [ ] 9.9 Whistleblower drafting.
- [ ] 9.10 Contract drafting capability.
- [ ] 9.11 Contract review capability.
- [ ] 9.12 Full postal To address.
- [ ] 9.13 To email address.
- [ ] 9.14 Full postal CC addresses.
- [ ] 9.15 CC email addresses.
- [ ] 9.16 User address correction.
- [ ] 9.17 Address verification workflow.
- [ ] 9.18 User correction submission to Janavani.
- [ ] 9.19 Expert/source verification.
- [ ] 9.20 PDF export.
- [ ] 9.21 DOCX export.
- [ ] 9.22 Submission instructions.
- [x] 9.24 Lock non-delivery boundary: Janavani generates/downloads documents; citizen sends them.
- [x] 9.25 Move WebApp/Telegram production document payload generation off durable artifact storage into an ephemeral response path; true device-local rendering remains open.
- [ ] 9.26 Verify PDF/DOCX payload never enters durable Janavani storage, logs, telemetry or backups across every remaining compatibility/legacy path; primary WebApp/Telegram/constitutional paths are now ephemeral.
- [x] 9.27 Add end-to-end citizen-download/self-send verification evidence for the primary WebApp path; extend to Telegram and constitutional paths.
- [ ] 9.23 Draft quality review.
- [ ] 9.24 Legal-information disclaimer and qualified-professional escalation where appropriate.

# 10. USER CORRECTIONS & KNOWLEDGE CONTRIBUTION

**Status: NOT STARTED**
- [ ] 10.1 Submit correction.
- [ ] 10.2 Attach supporting evidence.
- [ ] 10.3 Compare against authoritative sources.
- [ ] 10.4 Expert review.
- [ ] 10.5 Volunteer review.
- [ ] 10.6 Institutional review.
- [ ] 10.7 Confidence/status model.
- [ ] 10.8 Accept/reject/needs-review states.
- [ ] 10.9 Contributor attribution preference.
- [ ] 10.10 Correction history.
- [ ] 10.11 Gamification safeguards.

# 11. GOVERNMENT OFFICE / OFFICER / REPRESENTATIVE ACCOUNTABILITY

**Status: NOT STARTED — PARTIAL MODULES EXIST**
- [ ] 11.1 Office directory.
- [ ] 11.2 Officer directory.
- [ ] 11.3 Department directory.
- [ ] 11.4 MP directory.
- [ ] 11.5 MLA directory.
- [ ] 11.6 Office review capability.
- [ ] 11.7 Officer review capability.
- [ ] 11.8 Public-service performance metrics.
- [ ] 11.9 Central-government evaluation.
- [ ] 11.10 State-government evaluation.
- [ ] 11.11 Complaint outcome tracking.
- [ ] 11.12 Misbehaviour report workflow.
- [ ] 11.13 Corruption complaint workflow.
- [ ] 11.14 Transfer-before-minimum-service concern workflow.
- [ ] 11.15 Department-head escalation.
- [ ] 11.16 Administrative-head escalation.
- [ ] 11.17 MP/MLA representation workflow.
- [ ] 11.18 Defamation/false-allegation safeguards.
- [ ] 11.19 Evidence requirements.
- [ ] 11.20 Right-of-response mechanism.

# 12. GOVERNMENT SCHEMES & BENEFITS INTELLIGENCE

**Status: NOT STARTED**
- [ ] 12.1 Central schemes database.
- [ ] 12.2 State schemes database.
- [ ] 12.3 Eligibility rules.
- [ ] 12.4 Required documents.
- [ ] 12.5 Application process.
- [ ] 12.6 Official-source verification.
- [ ] 12.7 Source date/version.
- [ ] 12.8 Scheme change alerts.
- [ ] 12.9 Citizen eligibility assistance.
- [ ] 12.10 Benefit discovery.
- [ ] 12.11 Multilingual explanation.

# 13. RTI / EVIDENCE / CIVIC LEGAL WORKFLOW

**Status: NOT STARTED — PARTIAL DOCUMENT/AI SUPPORT**
- [ ] 13.1 RTI drafting.
- [ ] 13.2 PIO address lookup.
- [ ] 13.3 First appeal workflow.
- [ ] 13.4 Source/citation capture.
- [ ] 13.5 Evidence package generation.
- [ ] 13.6 Evidence integrity metadata.
- [ ] 13.7 BSA-related evidence-information support where applicable.
- [ ] 13.8 Legal review safeguards.

# 14. WHISTLEBLOWER SYSTEM

**Status: NOT STARTED**
- [ ] 14.1 Secure submission.
- [ ] 14.2 Optional anonymity/pseudonymity.
- [ ] 14.3 Threat model.
- [ ] 14.4 Metadata minimisation.
- [ ] 14.5 Evidence encryption.
- [ ] 14.6 Secure case identifier.
- [ ] 14.7 Source/provenance.
- [ ] 14.8 Reviewer access control.
- [ ] 14.9 Retaliation-risk handling.
- [ ] 14.10 Escalation workflow.
- [ ] 14.11 Legal/regulatory review.

# 15. EXPERT / VOLUNTEER / NGO / INSTITUTION ECOSYSTEM

**Status: NOT STARTED**
- [ ] 15.1 Individual registration.
- [ ] 15.2 Expert registration.
- [ ] 15.3 Society/community registration.
- [ ] 15.4 NGO registration.
- [ ] 15.5 Institution registration.
- [ ] 15.6 Verification levels.
- [ ] 15.7 Domain expertise registry.
- [ ] 15.8 Review assignment.
- [ ] 15.9 Conflict-of-interest declaration.
- [ ] 15.10 Reputation/quality scoring.
- [ ] 15.11 Permission control.

# 16. JNV-CAP-SOS — PERSONAL SAFETY

**Status: ARCHITECTURE LOCKED — IMPLEMENTATION NOT VERIFIED**
- [ ] 16.1 SOS data contract.
- [ ] 16.2 SOS routing engine.
- [ ] 16.3 Trusted contacts.
- [ ] 16.4 Friend/relative notification.
- [ ] 16.5 Optional authority notification.
- [ ] 16.6 Silent SOS.
- [ ] 16.7 Temporary live location.
- [ ] 16.8 User-defined escalation.
- [ ] 16.9 I'm Safe cancellation.
- [ ] 16.10 Delivery state machine.
- [ ] 16.11 Offline queue.
- [ ] 16.12 Retry engine.
- [ ] 16.13 Emergency packet priority.
- [ ] 16.14 Cryptographic integrity.
- [ ] 16.15 Replay protection.
- [ ] 16.16 Abuse/rate limiting.
- [ ] 16.17 Emergency resilience test suite.

# 17. JNV-CAP-SOS — MESH TRANSPORT

**Status: ARCHITECTURE LOCKED — IMPLEMENTATION NOT VERIFIED**
- [ ] 17.1 Transport abstraction.
- [ ] 17.2 Reticulum adapter.
- [ ] 17.3 LoRa/RNode integration assessment.
- [ ] 17.4 Meshtastic adapter assessment.
- [ ] 17.5 Local Bluetooth/Wi-Fi transport assessment.
- [ ] 17.6 Multi-hop routing.
- [ ] 17.7 Community relay node architecture.
- [ ] 17.8 Connected gateway architecture.
- [ ] 17.9 Store-and-forward.
- [ ] 17.10 Route failover.
- [ ] 17.11 Congestion/priority handling.
- [ ] 17.12 Field testing.

# 18. JNV-CAP-SOS — SATELLITE TRANSPORT

**Status: ARCHITECTURE LOCKED — IMPLEMENTATION NOT VERIFIED**
- [ ] 18.1 Satellite adapter contract.
- [ ] 18.2 Native device satellite capability assessment.
- [ ] 18.3 Companion satellite communicator assessment.
- [ ] 18.4 Provider abstraction.
- [ ] 18.5 Community satellite gateway architecture.
- [ ] 18.6 Satellite delivery state.
- [ ] 18.7 Sky-view/availability UX.
- [ ] 18.8 India regulatory review.
- [ ] 18.9 India device/service certification review.
- [ ] 18.10 Emergency-service integration review.
- [ ] 18.11 Field testing.

# 19. GOVERNMENT EMERGENCY ALERTS

**Status: ARCHITECTURE LOCKED — IMPLEMENTATION NOT VERIFIED**
- [ ] 19.1 Opt-in/opt-out preference.
- [ ] 19.2 Location selection.
- [ ] 19.3 Severity selection.
- [ ] 19.4 Official-source authentication.
- [ ] 19.5 Alert provenance.
- [ ] 19.6 Alert expiry/update handling.
- [ ] 19.7 Multilingual rendering.
- [ ] 19.8 AI explanation separated from official alert.
- [ ] 19.9 Internet distribution.
- [ ] 19.10 Mesh distribution.
- [ ] 19.11 Satellite/community distribution where authorised.

# 20. EVIDENCE / PROVENANCE / BLOCKCHAIN / DECENTRALIZATION

**Status: ARCHITECTURE DEFINED — IMPLEMENTATION NOT VERIFIED**
- [ ] 20.1 Evidence object model.
- [ ] 20.2 Cryptographic hashing.
- [ ] 20.3 Timestamp/provenance.
- [ ] 20.4 Chain of custody metadata.
- [ ] 20.5 Archive storage.
- [ ] 20.6 Optional blockchain anchoring.
- [ ] 20.7 Blockchain-independent fallback.
- [ ] 20.8 Optional Freenet storage/distribution.
- [ ] 20.9 Decentralized transport evaluation.
- [ ] 20.10 Verification tool.

# 21. FINANCIAL TRANSPARENCY & CONTRIBUTIONS

**Status: ARCHITECTURE DEFINED — IMPLEMENTATION NOT VERIFIED**
- [ ] 21.1 Live operating expenditure dashboard.
- [ ] 21.2 Expense categories.
- [ ] 21.3 Detailed head-wise expenditure.
- [ ] 21.4 Operating reserve policy.
- [ ] 21.5 Contribution mechanism.
- [ ] 21.6 Contributor public-display controls.
- [ ] 21.7 Name-only display.
- [ ] 21.8 Name + photo display.
- [ ] 21.9 Name + photo + amount display.
- [ ] 21.10 Anonymous + amount display.
- [ ] 21.11 Full disclosure on demand subject to applicable law/privacy.
- [ ] 21.12 Public financial reporting.
- [ ] 21.13 Audit trail.
- [ ] 21.14 Restricted/unrestricted funds separation.

# 22. CHANNEL ECOSYSTEM

**Status: DESIGN — IMPLEMENTATION NOT VERIFIED**
- [ ] 22.1 Dynamic Web app.
- [ ] 22.2 Android app.
- [ ] 22.3 iOS app.
- [ ] 22.4 Telegram Bot.
- [ ] 22.5 Telegram Mini App.
- [ ] 22.6 WhatsApp integration.
- [ ] 22.7 Messenger integration.
- [ ] 22.8 Web3 DApp.
- [ ] 22.9 Channel capability parity matrix.
- [ ] 22.10 Channel-specific offline behavior.
- [ ] 22.11 Channel failure isolation.

# 23. WEB3 / DECENTRALIZED ECOSYSTEM

**Status: DESIGN — IMPLEMENTATION NOT VERIFIED**
- [ ] 23.1 DApp architecture.
- [ ] 23.2 Wallet/identity strategy.
- [ ] 23.3 Decentralized evidence verification.
- [ ] 23.4 Optional blockchain anchoring.
- [ ] 23.5 Decentralized storage evaluation.
- [ ] 23.6 Freenet integration evaluation.
- [ ] 23.7 Governance safeguards.
- [ ] 23.8 Web3-independent core fallback.

# 24. SECURITY / PRIVACY / TRUST

**Status: NOT STARTED — PARTIAL CONTROLS EXIST**
- [ ] 24.1 Threat model.
- [ ] 24.2 Privacy model.
- [ ] 24.3 Data minimisation.
- [ ] 24.4 Encryption at rest.
- [ ] 24.5 Encryption in transit.
- [ ] 24.6 Key management.
- [ ] 24.7 Access audit.
- [ ] 24.8 Abuse prevention.
- [ ] 24.9 Account recovery.
- [ ] 24.10 Whistleblower threat model.
- [ ] 24.11 SOS threat model.
- [ ] 24.12 AI safety model.
- [ ] 24.13 Supply-chain security.

# 25. TESTING & QUALITY ASSURANCE

**Status: NOT STARTED — TEST ASSETS EXIST; EXECUTION EVIDENCE PENDING**
- [ ] 25.1 Unit tests.
- [ ] 25.2 Integration tests.
- [ ] 25.3 End-to-end tests.
- [ ] 25.4 Offline tests.
- [ ] 25.5 Failure-injection tests.
- [ ] 25.6 AI-provider failure tests.
- [ ] 25.7 Database failure tests.
- [ ] 25.8 Messaging-channel failure tests.
- [ ] 25.9 Mesh failure tests.
- [ ] 25.10 Satellite failure tests.
- [ ] 25.11 Blockchain/Freenet failure tests.
- [ ] 25.12 Security testing.
- [ ] 25.13 Privacy testing.
- [ ] 25.14 Accessibility testing.
- [ ] 25.15 Multilingual testing.
- [ ] 25.16 Disaster/resilience testing.
- [ ] 25.17 Human expert acceptance testing.

# 26. DOCUMENTATION & OPERATIONS

**Status: IN PROGRESS — CANONICAL FOUNDATION EXISTS**
- [x] 26.1 Master architecture document.
- [x] 26.2 Master task checklist.
- [x] 26.3 Capability registry — DESIGN COMPLETE.
- [x] 26.4 Data contracts — DESIGN COMPLETE.
- [ ] 26.5 API documentation.
- [ ] 26.6 Deployment documentation.
- [ ] 26.7 Security documentation.
- [ ] 26.8 Privacy documentation.
- [ ] 26.9 Disaster recovery documentation.
- [ ] 26.10 Incident response documentation.
- [ ] 26.11 Contribution governance.
- [ ] 26.12 Archive index.

# 27. ARCHIVE & RECORD MANAGEMENT

**Status: POLICY LOCKED — IMPLEMENTATION NOT STARTED**
- [ ] 27.1 Archive policy.
- [ ] 27.2 Archive directory structure.
- [ ] 27.3 Deprecated-version index.
- [ ] 27.4 Migration records.
- [ ] 27.5 Retention periods by data class.
- [ ] 27.6 Legal hold mechanism where required.
- [ ] 27.7 Privacy-driven deletion mechanism where required.
- [ ] 27.8 Archive integrity verification.

---

# 28. MASTER EXECUTION QUEUE

**Queue control rule:** Execute only unresolved items. Do not repeat an audit already evidenced in the latest status/audit records.

## M2 — REPOSITORY RUNTIME / DEPENDENCY RECONCILIATION

- [x] M2-A Static repository/tree/runtime-import/deployment mapping substantially completed.
- [x] M2-C Storage reconnaissance completed; ownership decisions remain open.
- [ ] M2-B Capability → Repository → Test → Deployment Map.
- [ ] M2-C Storage Ownership Map — decision/verification layer.
- [ ] M2-D Runtime Execution Verification.

## P0 — CURRENT CONVERGENCE GATE (2026-09-19)

Architectural decision: Janavani owns the capability; PostgreSQL is the relational standard; Supabase is not required by runtime, build, CI, configuration or startup. Historical Supabase artifacts remain in archive/legacy/ only.

- [x] P0.1 Active Supabase implementation files removed from runtime graph and preserved in archive.
- [x] P0.2 Supabase package removed from requirements.txt and pyproject.toml.
- [x] P0.3 Supabase runtime configuration removed from src/core/config.py and .env.example.
- [x] P0.4 Civic Case provider selection reduced to memory / postgres.
- [x] P0.5 Sweep active imports/build/configuration/tests and move canonical SQL migrations to provider-neutral db/migrations/. Historical Supabase references remain only in dated evidence/archive; deployment/startup verification remains open.
- [ ] P0.6 Run canonical PostgreSQL conformance/security gate and record exact CI evidence.

### PostgreSQL conformance/security gate

- [x] P0.6a Atomic Case + event/reference transaction boundary exists.
- [x] P0.6b Rollback test exists.
- [x] P0.6c Stale-version concurrency rejection test exists.
- [x] P0.6d Submission/Case exact replay/idempotency integration test exists.
- [ ] P0.6e Cross-user negative authorization tests execute against real PostgreSQL.
- [ ] P0.6f PostgreSQL RLS policies are implemented and negative-tested; candidate policy now explicitly FORCEs RLS on protected tables.
- [ ] P0.6g Restart durability / outage / recovery evidence is executed.
- [ ] P0.6h Backup/restore evidence is executed.

## Immediate unresolved sequence

1. P0.6 PostgreSQL conformance/security gate: execute real cross-user authorization + candidate RLS tests; keep RLS unactivated until evidence passes.
2. Verify canonical Web/API runtime and independent surface startup evidence.
4. P0.6g/P0.6h restart, outage/recovery and backup/restore evidence.
5. M2-B Capability → Repository → Test → Deployment Map.
6. M2-C Storage Ownership decision/verification layer.
7. Only then approve targeted consolidation/archive candidates.


1. P0.6 PostgreSQL conformance/security gate: execute real cross-user authorization + candidate RLS tests; keep RLS unactivated until evidence passes.
2. P0.6g/P0.6h restart, outage/recovery and backup/restore evidence.
3. M2-D Runtime Execution Verification: canonical Web/API, CI and independent surface startup evidence.
4. M2-B Capability → Repository → Test → Deployment Map.
5. M2-C Storage Ownership decision/verification layer.
6. Only then approve targeted consolidation/archive candidates.

## Ecosystem construction sequence after reconciliation

5. Identity/permission foundations.
6. Evidence/provenance foundations.
7. Canonical document engine.
8. Government information/source layer.
9. Core civic capabilities.
10. Accountability/knowledge contribution.
11. SOS + resilient transport.
12. Distributed/Web3 capabilities.
13. Full channel integrations and parity verification.
14. System-wide testing, security, privacy, resilience and operational hardening.

---

# 29. COMPLETION GATE

A master task may move to `COMPLETE` only when applicable evidence shows:

- [ ] Implementation exists.
- [ ] Repository file(s) verified.
- [ ] Tests pass.
- [ ] Failure behavior tested.
- [ ] Security/privacy requirements checked.
- [ ] User workflow verified.
- [ ] Relevant expert/source review completed.
- [ ] Documentation updated.
- [ ] Commit/PR evidence recorded.
- [ ] No unresolved critical dependency remains.

For design-only work, use `DESIGN COMPLETE` and record:

- design document exists;
- contract/metadata is defined;
- dependencies/open questions are recorded;
- implementation is explicitly not implied.

---

# 30. ARCHIVE CONTROL

No archive operation is authorised by this checklist merely because a file is old, duplicated, experimental or superseded-looking.

Archive requires:

1. no active dependency;
2. no required runtime path;
3. no irreplaceable data;
4. replacement exists where required;
5. tests pass after deprecation/removal where applicable;
6. historical value is preserved;
7. archive location and reason are recorded.

---

# 31. CHANGE LOG

| Date | Change | Evidence |
|---|---|---|
| 2026-08-23 | Master architecture locked | `docs/JANAVANI_MASTER_ARCHITECTURE.md` |
| 2026-08-23 | Capability registry created — design complete | `docs/CAPABILITY_REGISTRY.md` + status register |
| 2026-08-23 | Core data contracts created — design complete | `docs/DATA_CONTRACTS.md` + status register |
| 2026-08-23 | Static repository reconciliation substantially completed | dated reconciliation/runtime audits |
| 2026-08-23 | Storage reconnaissance completed | `docs/STORAGE_OWNERSHIP_MAP_2026-08-23.md` / storage evidence |
| 2026-08-23 | Ecosystem scope explicitly locked as NOT MVP | `docs/JANAVANI_ECOSYSTEM_CHARTER.md` + documentation correction record |
| 2026-09-19 | PostgreSQL became the canonical relational standard; active Supabase runtime/build dependency removed and historical evidence archived | `docs/audits/POSTGRESQL_STANDARD_SUPABASE_CONVERGENCE_2026-09-19.md` |
| 2026-09-20 | CI supply-chain hardening: CodeQL, OpenSSF Scorecard, pinned action baselines, SBOM and build/SBOM attestations | `.github/workflows/security-ci.yml`, `.github/workflows/docker-publish.yml` |
| 2026-09-20 | PostgreSQL RLS integration gate expanded with non-BYPASSRLS roles, delegation expiry/revocation, DELETE denial, and transaction-local principal context isolation | `tests/test_candidate_rls_authorization_integration.py` |
| 2026-09-20 | Candidate RLS hardened with FORCE ROW LEVEL SECURITY on protected tables; production activation remains blocked pending real-PostgreSQL evidence | `db/migrations/CANDIDATE_20260919_rls_authorization.sql` |
| 2026-09-20 | PostgreSQL security gate prioritized ahead of broader capability mapping | Current master execution queue |
| 2026-09-22 | Purpose-bound capability session lifecycle implemented as shared ecosystem infrastructure; platform-specific permission/revocation verification remains open | `src/access/capability_session.py`, `tests/test_capability_session.py`, `docs/architecture/CAPABILITY_SESSION_CONTRACT.md` |
| 2026-10-05 | AI provider dependency boundary centralized: concrete OpenRouter/Hugging Face providers are composed only in `src/ai/composition.py`; Translation and legal drafting consume provider-neutral contracts | `src/ai/composition.py`, `src/capabilities/translation.py`, `src/services/legal_agent.py` |
| 2026-08-23 | Checklist reconciled against verified status register | `docs/MASTER_TASK_CHECKLIST_RECONCILIATION_2026-08-23.md` |

---

# MASTER RULE

> **Nothing is considered finished because it was discussed. Nothing is considered finished because code was written. Design completion is not implementation completion. A Janavani capability is finished only when its implementation, dependencies, failure modes, verification, documentation, security/privacy requirements and evidence are all satisfied.**

**END — MASTER TASK CHECKLIST**


# 32. EXECUTION RESET — 2026-10-07

## Branch governance

- [x] Exactly nine active branches verified.
- [x] `main` remains canonical default branch.
- [x] No tenth feature branch authorized.
- [x] Useful branch work must be verified before integration/retirement.
- [x] Branch deletion is not required now because the repository already satisfies the nine-branch target.

## Programming audit

- [x] Shared capability boundary verified.
- [x] Shared surface composition verified.
- [x] Web adapter boundary verified.
- [x] Telegram adapter/bootstrap boundary verified.
- [x] Cross-surface Case contract tests identified.
- [x] Responsibility split rule reaffirmed: split only at real architectural boundaries.
- [ ] PostgreSQL cross-user authorization/RLS evidence on real PostgreSQL.
- [ ] Restart/outage/recovery evidence.
- [ ] Backup/restore evidence.
- [ ] Canonical Web/API runtime evidence.
- [ ] Independent Telegram runtime evidence.

## Build priority

### P1 — Shared civic-action vertical slice

- [x] Case capability shared by Web and Telegram composition.
- [x] Authority capability shared by Web and Telegram composition.
- [x] Evidence capability shared by Web and Telegram composition.
- [x] Document review/drafting boundaries exist.
- [x] Consent capability exists in the shared graph.
- [ ] Complete runtime-verified issue → Case → authority → evidence → document → review → consent → submission-preparation → tracking flow on Web.
- [ ] Complete the same flow on Telegram without duplicating business logic.
- [ ] Cross-surface continuation verified with real persistence and identity policy.

### P2 — Surface parity

- [ ] WebApp and Telegram use the same canonical lifecycle and capability contracts in deployed environments.
- [ ] Failure of either surface leaves the other operational.
- [ ] Runtime/provider configuration is independently verifiable per surface.

### P3 — Ecosystem expansion after P1/P2 gates

- [ ] Telegram Mini App.
- [ ] WhatsApp/Messenger adapters.
- [ ] Android/iOS surfaces.
- [ ] DApp/Web3 capabilities where justified.
- [ ] Expanded AI/Agentic AI capabilities.
- [ ] Resilient/decentralized transports.

## Architectural split rule

Split code only when the split creates an independent boundary of change ownership, trust/security, persistence/provider dependency, independent reuse, independently testable lifecycle/state, or external transport/provider dependency. Preserve cohesive code when splitting would duplicate orchestration or weaken invariants.

## Audit evidence

- docs/90-audits/2026-10-07-quick-programming-audit-and-execution-reset.md


# 33. ENGINEERING PROOF CYCLE — 2026-10-08

## Current verified state

- [x] Exactly nine active branches verified on GitHub.
- [x] No tenth branch created.
- [x] Current main proof-cycle decision record committed: `docs/90-audits/2026-10-08-engineering-proof-cycle-reset.md`.
- [x] Current Vercel status for proof-cycle commit `fe64478b5cb327f4140672a10ee313e94bf1bdef` is SUCCESS.
- [ ] Fresh GitHub Actions evidence for that commit.
- [ ] Real PostgreSQL production-style recovery evidence.
- [ ] Backup/restore evidence.
- [ ] Independent deployed Web/API runtime evidence.
- [ ] Independent deployed Telegram runtime evidence.

## Branch disposition rule

No branch is deleted merely because it is old or divergent. The repository already satisfies the exact-nine invariant. Divergent branches must be selectively mined for still-valid unique work, verified against current contracts, and only then retired when safe branch-deletion capability and evidence are available.

## Proof-cycle architecture freeze

No new universal orchestration layer or duplicate capability implementation is authorized during this cycle.

Split only when there is an independent boundary of:
- change ownership;
- trust/security;
- persistence;
- provider dependency;
- independent reuse;
- independently testable lifecycle/state;
- external transport/provider dependency.

Preserve cohesion when splitting would duplicate orchestration, fragment invariants, or create competing sources of truth.

## Evidence gate order

1. Canonical correctness: Web vertical slice, Web/Telegram shared capability contract, Python/Rust parity, transaction/concurrency.
2. PostgreSQL: cross-user RLS isolation, authorization denial, rollback/atomicity, restart/recovery, backup/restore.
3. Runtime independence: Web/API and Telegram startup, health, provider configuration and failure isolation.
4. Security/privacy: authorization, consent, expiry/revocation, content persistence boundary, redaction and non-durable document artifacts.

## Release rule

Green static analysis or CI alone is not production certification. Production readiness requires runtime/deployment evidence for every applicable gate above.



---

# 34. CURRENT EXECUTION REBASELINE — 11 OCTOBER 2026

**This section supersedes older status statements where they conflict with current live evidence.** Older checklist sections remain as historical records; their branch-count claims must not be read as the current state.

## Site roles — owner-confirmed

- [x] Primary public site for current use: https://netzen-abm.github.io/janavani/
- [x] Separate brochure/showcase site: https://netzen-abm.github.io/janavani-website/
- [x] Public repository README on the review branch now distinguishes these roles.
- [x] A static, responsive primary-site landing page has been added as root `index.html` on the existing review branch. Until `/app` is deployed and verified, the page links to the civic-action explainer and showcase rather than to an unavailable workspace route.
- [ ] After merge, confirm the GitHub Pages publishing source for `netzen-abm/janavani` is configured to publish the branch/root containing `index.html`; verify deployed metadata, links, mobile layout, keyboard access and reduced-motion behavior.
- [ ] Keep the brochure repository's page canonicals and sitemap pointing to its own `/janavani-website/` URLs. Do not conflate its SEO identity with the primary site's URL.
- [ ] Keep the `/app` route out of public CTAs until a merged main deployment returns a successful runtime check; afterward label it as an early local-drafting preview, not a complete WebApp.

## Branch hygiene — current live state

- [ ] **BLOCKED: exact-nine invariant.** The current GitHub branch query returned 10 physical branches, including `audit/2026-10-11-live-rebaseline`.
- [ ] Run `.github/workflows/branch-retirement.yml` from `main` with `execute=true` and confirmation `RETIRE-LEGACY-BRANCHES`. The workflow must archive the extra branch head before deleting its ref; do not delete one of the nine approved branch roles to satisfy the count.
- [ ] Re-query GitHub branches after workflow completion and require exactly nine physical refs before marking the invariant complete.
- [ ] Do not create an additional branch. Continue work on `chore/ecosystem-shared-capability-infrastructure` until the current reviewed changes are either merged or explicitly retired.

## Proof-and-product gates

- [ ] Finish fresh CI after the landing page and checklist/readme updates.
- [ ] Verify current default CodeQL analysis on the review head; custom Security CI is not a substitute for CodeQL coverage.
- [ ] Verify the live primary Pages URL renders the new landing page after deployment.
- [ ] Configure and verify the independent Telegram Worker in Render; a `render.yaml` worker definition is not deployment evidence.
- [ ] Complete the shared civic-action workflow across Web and Telegram with real identity, authorization, persistence and explicit consent.
- [ ] Keep PostgreSQL RLS, least-privilege database role, migration/rollback, transaction atomicity, restart/recovery and backup/restore as release gates.

## Responsibility rule

No extra abstractions or arbitrary file-size refactors during the proof cycle. Keep domain invariants and cohesive orchestration together. Separate code only where the separation creates a real boundary of change ownership, trust/security, persistence, provider dependency, independent reuse, lifecycle/state testing or external transport.

## EXECUTION LOG — 12 OCTOBER 2026

### Telegram reliability proof cycle
- [x] Confirm exactly nine approved active branches.
- [x] Bound Telegram webhook request bodies to 1 MiB and validate declared plus streamed size.
- [x] Preserve pending updates in the polling startup path with `drop_pending_updates=False`.
- [x] Add a PostgreSQL durable inbox migration keyed by Telegram `update_id`, with bounded retry/dead-letter state and terminal payload clearing.
- [x] Add a PostgreSQL inbox adapter using `FOR UPDATE SKIP LOCKED`, plus processing-lease renewal and worker dispatch.
- [x] Wire production webhook startup to require `JANAVANI_TELEGRAM_INBOX_DSN`; acknowledge only after the durable insert/duplicate check returns.
- [x] Add route tests for durable acceptance and retryable failure; document the delivery contract and deployment prerequisites.
- [ ] Apply the new inbox migration to a disposable PostgreSQL database and run end-to-end worker/restart tests.
- [ ] Verify latest CI for the new inbox commits and resolve all failures.
- [ ] Add explicit least-privilege database grants for the deployment role and verify them against the live service configuration.
- [ ] Prove business-operation idempotency where a handler effect can occur before inbox completion is recorded.
- [ ] Verify deployed Telegram and Web/API runtimes independently; do not infer production readiness from CI alone.

**Delivery semantics:** Durable at-least-once delivery to handler dispatch is the target. Exactly-once business effects are not claimed. The WebApp remains browser-local drafting until authenticated, persistent Case operations are demonstrated.


---

# 35. ENGINEERING PROOF CYCLE — 15 OCTOBER 2026

**Current review branch:** `chore/ecosystem-shared-capability-infrastructure`  
**Current known head at prior evidence capture:** `3d38c2fadce3691eeb9b370d86c839f607234432`  
**PR:** [#204](https://github.com/netzen-abm/janavani/pull/204) — keep draft and unmerged until acceptance gates pass.

## Live repository and CI recheck

- [x] GitHub branch inventory returns exactly nine physical branches: `main`, `integration/canonical-platform`, `feat/canonical-case-kernel`, `feat/canonical-capability-execution-envelope`, `feat/canonical-civic-action-vertical-slice`, `feat/canonical-sos-contract`, `feat/capability-scoped-consent-agent-enforcement`, `audit/postgres-provider-production-gates`, and `chore/ecosystem-shared-capability-infrastructure`.
- [x] Branch-budget job passed in workflow run `38616728218`.
- [x] Focused test job passed in run `38616728218`, including syntax, active-source line guard, smoke tests, Web vertical slice, Web/Telegram shared-capability gate, live PostgreSQL RLS isolation, identity pairing, Telegram inbox, backup/restore, and PostgreSQL restart durability.
- [x] Docker build run `38616728412` passed.
- [x] Dependency Review run `38616728976` passed.
- [ ] **Full canonical suite is NOT green:** canonical-suite job `116033592567` in run `38616728218` ended `cancelled`. Cancellation is neither pass nor a diagnosed test failure. Obtain a fresh, completed run and investigate the reason for cancellation before release decisions.

## P0 — prove Telegram business-effect replay safety

- [x] Acceptance contract exists: `docs/architecture/TELEGRAM_POST_COMMIT_REPLAY_ACCEPTANCE_CONTRACT.md`.
- [x] Existing PostgreSQL inbox tests cover durable acceptance, duplicate Telegram update ID, claim completion, and stale-worker fencing.
- [x] Existing PostgreSQL submission/Case transaction test covers atomic projection/event mutation and repository-level idempotent replay.
- [ ] Add a PostgreSQL-backed failure-injection test through the actual Telegram handler/capability and durable transaction path: commit business mutation, inject failure before inbox completion, reclaim/redeliver, then assert one durable Case/Submission mutation, one lifecycle event, safe/deduplicated consequential effects, and eventual inbox completion.
- [ ] Re-run with fresh worker/repository instances and reject conflicting reuse of the business idempotency key.
- [ ] Record CI evidence proving this test actually executed against PostgreSQL and was not skipped.

**Do not treat the acceptance document or separate inbox/repository tests as proof of the combined crash window.** Inbox delivery remains at-least-once; the target is effectively-once business effects through the existing durable idempotency boundary, not exactly-once delivery.

## P1 — Web ↔ Telegram end-to-end continuity

- [ ] Verify Web creates a durable Case through authenticated API operations.
- [ ] Verify a paired Telegram identity can retrieve and continue that same Case after process restart.
- [ ] Verify a different identity is denied access.
- [ ] Verify consent, evidence/document references, submission preparation and lifecycle history remain consistent across both surfaces.
- [ ] Verify Web/API and Telegram worker can fail/restart independently without losing accepted updates or committed Case state.

## Architecture and operations constraints

- Exactly nine physical branches; do not create a tenth branch for this cycle.
- Archive before retiring any branch; no branch retirement is currently required by the verified inventory.
- Preserve existing domain/capability orchestration. Do not introduce another generic idempotency layer.
- Separate only at transport/trust, persistence/provider, independent runtime, or independently reusable/testable lifecycle boundaries.
- Keep `/app` described as local drafting until authenticated durable Case operations and cross-surface continuity are demonstrated.
- Keep PR #204 draft/unmerged and do not promote production based on focused gates alone.

## Next two engineering actions

1. Investigate why the canonical suite was cancelled and obtain a completed result.
2. Implement and execute the PostgreSQL-backed Telegram post-commit crash/redelivery test through the real handler and canonical capability path.

---

# 36. CURRENT ENGINEERING PROOF CYCLE — 25 OCTOBER 2026

**Status:** IN PROGRESS — current rebaseline; this section supersedes older statements about the current branch target and release status. Historic entries remain for audit history.

## Verified repository baseline

- [x] Current audit recorded in `docs/90-audits/2026-10-25-engineering-proof-cycle-and-repository-structure-audit.md`.
- [x] Current source tree and responsibility boundaries reviewed; no bulk file moves or architecture-generation branch created.
- [x] Current public review line retained as `chore/ecosystem-shared-capability-infrastructure`; no new branch created.
- [x] Issues #217, #218, and #219 created and linked to PR #204.
- [ ] **Branch target: exactly eight physical refs.** Last live query returned nine refs, including `feat/canonical-capability-execution-envelope` as the temporary retirement-only transition branch.
- [ ] Correct the active GitHub `main` ruleset: it currently requires zero approving reviews while the written policy requires an independent approval.
- [ ] Merge PR #213 only after independent review and the actual ruleset/policy mismatch is resolved; then allow the guarded archive/delete workflow to finish and re-query GitHub for exactly eight physical refs.
- [ ] Eventual single-branch state: `main` only, after full product-readiness acceptance and archive-before-delete review.

- [ ] **Issue #221 — Vercel production configuration audit:** production is reported READY at main SHA `7bb10a881601c24e99f2deb1b98ce84266259ee8`; project metadata reports `flask`, while the repository's canonical entry point is FastAPI. Verify actual project settings/build logs and production env presence after owning-team authorization; test a FastAPI preview before changing preset. Do not remove Flask blindly because WhatsApp/Messenger modules import it, and do not promote PR #204 based on preview metadata.

## P0 — Security, privacy, and correctness proofs

- [ ] **Issue #219 — Telegram inbox privacy:** full update JSON remains in PostgreSQL during pending/processing/retry states. The `/start` and `/privacy` disclosures are now corrected in this review branch, including the worker-offline retention gap. This is disclosure-only; decide the approved data/retention policy and add live-PostgreSQL positive/negative tests before calling the privacy issue closed.
- [x] **Issue #220 — WebApp legacy constitutional bill-review flow: fail-closed interim decision recorded.** The GET route now explains the source-provenance blocker (HTTP 503), and the retired POST route returns HTTP 410; prior workflow intent and reactivation criteria are preserved in `archive/documentation/legacy/2026-10-25-webapp-constitutional-bill-review-route.md`. Regression tests are added; keep the issue open until current-head CI passes. Do not reactivate until source-backed bill profiles, owned objection Case, verified authority, safe download headers, privacy and end-to-end acceptance are proven.
- [ ] **Issue #217 — Telegram post-commit replay:** execute real handler/shared capability against PostgreSQL; inject failure after committed business mutation but before inbox completion; replay with a fresh worker; assert one durable mutation/event, safe side-effect deduplication, conflicting idempotency-key rejection and eventual inbox completion.
- [ ] **WebApp identity:** verify real OIDC issuer/client/session configuration, PKCE/state/nonce/JWKS validation, cookie behavior, API assertion checks, logout semantics and copied-cookie revocation/risk decision.
- [ ] **Independent runtime:** deploy and verify WebApp, canonical Web/API, and Telegram webhook separately. Record each service ID, commit SHA, URL, liveness and failure/restart result. Current Render inventory previously showed only the canonical API service.
- [ ] **Cross-surface acceptance:** prove authenticated Case create/retrieve in both directions, identity pairing, ownership isolation, document review, explicit consent, restart recovery and failure isolation.

## P1 — Toolchain and reproducibility

- [ ] **Issue #218:** choose one authoritative Python lock strategy compatible with current deployment.
- [ ] Decide and commit Rust `Cargo.lock` if appropriate for the workspace/application, and run checks/tests with locked dependency resolution.
- [ ] Add Rust workspace unit tests to required CI where crates contain executable/testable behavior.
- [ ] Establish a Ruff baseline and make the approved source-scope gate blocking; avoid a blind full-tree lint rewrite.
- [ ] Add static type checking selectively around identity, domain/application contracts and repository interfaces; preserve runtime validation for untrusted API input.
- [ ] Re-run current-head checks; prior green runs do not certify later commits.

## Architecture and file-organization guardrails

- [x] Keep canonical Case/lifecycle rules in shared capability/domain code.
- [x] Keep WebApp, Web/API, and Telegram transport adapters independent.
- [x] Keep provider-specific persistence behind storage/repository contracts.
- [x] Keep Case/Submission transaction ownership cohesive.
- [x] Keep citizen-authored content retention separate from Case metadata persistence.
- [x] Use normal Python/Rust/JavaScript language and runtime mechanisms; do not build custom constants/collections/type system/compiler/JIT/event loop/package runtime.
- [x] Use docs/README source-of-truth hierarchy and archive/historical folders; do not bulk-move source files without import/runtime proof.
- [ ] Record current-SHA CI plus deployed acceptance evidence before promoting PR #204.

## Webstudio / static-site / dynamic application decision

- [x] Preserve the existing static public website as the source-controlled design/content boundary unless a concrete redesign requirement justifies a migration.
- [x] Treat Webstudio as a visual authoring/export option, not as the owner of authentication, Case lifecycle or private citizen state.
- [x] Evaluate Cloudflare Pages for static public content and preview builds; evaluate Workers only when a specific dynamic edge/runtime need exists. Do not rewrite the Python API to match a host.
- [ ] Test any static export's generated paths, SEO metadata, CSP/security headers, forms, accessible interactions, mobile/reduced-motion behavior and API-link correctness before publishing.
- [ ] Keep authenticated WebApp state behind the trusted WebApp/API boundary; static export alone is not the completed application.

## Next two engineering actions

1. Resolve Issue #219's durable Telegram payload privacy/retention contract and add live-PostgreSQL coverage.
2. Close Issue #217's handler-level post-commit replay test, then run the deployed Web–API–Telegram acceptance runbook.

**Completion rule:** Do not mark a task complete because a doc exists, a PR is mergeable, CI passed on an older SHA, or a deployment file declares a service. Require current-SHA verification, failure-path evidence, privacy/security review, and applicable deployed-runtime acceptance.

