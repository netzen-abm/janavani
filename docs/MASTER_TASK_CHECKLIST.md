# 🇮🇳 JANAVANI — MASTER TASK CHECKLIST

**Status:** LIVE MASTER CONTROL DOCUMENT  
**Version:** 1.1  
**Date:** 23 August 2026  
**Scope:** COMPLETE JANAVANI ECOSYSTEM — NOT AN MVP

**Purpose:** Single authoritative checklist for tracking the complete Janavani ecosystem. It records master workstreams, subtasks, dependencies, verification status, and completion evidence.

> **Canonical scope rule:** Janavani is being built as a complete citizen-governance ecosystem. Web, Android, iOS, Telegram Bot, Telegram Mini App, WhatsApp, Messenger, DApp/Web3, AI/non-AI paths, resilient mesh and satellite capabilities are ecosystem surfaces/capabilities. Individual milestones are construction stages, not the product boundary.

> **Completion rule:** A task is not COMPLETE merely because code or documentation exists. Engineering completion requires implementation, tests, repository verification, security/privacy review where applicable, functional verification, and evidence. Design completion is explicitly labelled DESIGN COMPLETE and must not be confused with implementation completion.

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
- [ ] 1.10 Create permission/consent contracts.
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

**Status: NOT STARTED**

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

**Status: NOT STARTED — POC COMPONENTS EXIST**

- [ ] 8.1 AI provider abstraction.
- [ ] 8.2 Local/SLM capability assessment.
- [ ] 8.3 RAG architecture.
- [ ] 8.4 Source citation requirements.
- [ ] 8.5 Knowledge freshness policy.
- [ ] 8.6 LLM routing policy.
- [ ] 8.7 Agentic AI tool permissions.
- [ ] 8.8 Human approval gates.
- [ ] 8.9 AI failure fallback.
- [ ] 8.10 AI safety/evaluation suite.
- [ ] 8.11 Prompt/version registry.
- [ ] 8.12 Hallucination/error reporting.

# 9. CIVIC DOCUMENT & LETTER ENGINE

**Status: IN PROGRESS — ARCHITECTURE + PARTIAL IMPLEMENTATION**

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

## Immediate unresolved sequence

1. M2-B Capability → Repository → Test → Deployment Map.
2. M2-C Storage Ownership decision/verification layer.
3. M2-D Runtime Execution Verification.
4. Only then approve targeted consolidation/archive candidates.

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
| 2026-08-23 | Checklist reconciled against verified status register | `docs/MASTER_TASK_CHECKLIST_RECONCILIATION_2026-08-23.md` |

---

# MASTER RULE

> **Nothing is considered finished because it was discussed. Nothing is considered finished because code was written. Design completion is not implementation completion. A Janavani capability is finished only when its implementation, dependencies, failure modes, verification, documentation, security/privacy requirements and evidence are all satisfied.**

**END — MASTER TASK CHECKLIST**
