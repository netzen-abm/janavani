# 🇮🇳 JANAVANI — MASTER TASK CHECKLIST STATUS REGISTER

**Date:** 9 September 2026
**Purpose:** Reconcile the canonical Master Task Checklist against the latest Janavani architecture, repository-audit evidence, and project decisions.
**Authority:** `docs/MASTER_TASK_CHECKLIST.md` remains the canonical task inventory. This dated register updates execution priority/status; it does not replace the canonical checklist.

## 1. EXECUTIVE AUDIT

Janavani is architecturally strong but implementation is still materially behind the full ecosystem scope. The current priority is **convergence + verification + one complete civic-action vertical slice**, not creation of additional architectural generations.

Engineering planning estimate remains approximately **25–30% production-grade ecosystem readiness**. This is an engineering estimate, not a repository claim.

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
- [ ] Add explicit capability → repository → tests → CI/deployment evidence mapping.

### P0-B — GITHUB / REPOSITORY CONVERGENCE

- [ ] Establish current `main` runtime truth across Render/Vercel/Docker/local entry points.
- [ ] Verify actual API/service execution paths.
- [ ] Verify storage ownership and provider boundaries.
- [ ] Verify current AI/provider integrations.
- [ ] Verify SOS runtime claims before marking implementation complete.
- [ ] Audit branches/PRs for useful work; preserve before consolidation.
- [ ] Consolidate duplicate generations of lifecycle, consent, WebApp, storage, architecture guards and provider adapters.
- [ ] Archive superseded work with evidence; delete only after archive-readiness checks.
- [ ] Record GitHub SHA/PR/CI evidence for each completed convergence item.

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

- [ ] Create Case.
- [ ] Understand/structure citizen issue.
- [ ] Determine jurisdiction.
- [ ] Resolve responsible authority from verified sources.
- [ ] Collect/register local evidence.
- [ ] Preserve provenance/integrity metadata.
- [ ] Select civic action type.
- [ ] Generate document from canonical template.
- [ ] Allow user editing/correction.
- [ ] User explicitly approves final document.
- [ ] Generate PDF.
- [ ] Generate editable document where supported.
- [ ] Provide print/download/submission instructions.
- [ ] Keep submission as a separate explicit capability.
- [ ] Record acknowledgement/tracking when a submission mechanism exists.

### P0-F — WEBAPP REFERENCE CLIENT

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
- [ ] Migrate Telegram business logic to shared capability contracts.
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

1. M2-B Capability → Repository → Test → Deployment mapping.
2. M2-C Storage ownership decision/verification.
3. M2-D Runtime execution verification, including production entry-point truth.
4. Consolidate duplicate architecture/storage generations using archive-first evidence.
5. Complete canonical Identity + Consent runtime contracts.
6. Complete local Evidence + Provenance implementation and verification.
7. Implement Authority/Jurisdiction provider with source freshness/provenance.
8. Implement canonical Document/template engine with PDF + editable output and user correction.
9. Connect Case → Evidence → Authority → Document → Review into one tested vertical slice.
10. Build/verify the WebApp reference client against shared contracts, then converge Telegram.

## 7. STATUS INTERPRETATION

Use these states strictly:

- **COMPLETE:** implementation + tests + repository verification + required security/privacy review + functional/runtime evidence.
- **VERIFYING:** implementation exists but required evidence is incomplete.
- **DESIGN COMPLETE:** contract/architecture exists; implementation is not implied.
- **IN PROGRESS:** active implementation/convergence.
- **NOT STARTED:** no verified implementation.
- **BLOCKED:** dependency prevents execution.
- **ARCHIVED:** superseded material preserved with reason/evidence.

## 8. CHANGE LOG

| Date | Change |
|---|---|
| 2026-09-09 | Reconciled latest Janavani architecture/project history with canonical Master Task Checklist. |
| 2026-09-09 | Shifted execution frontier from architecture invention to convergence, verification and flagship civic-action vertical slice. |
| 2026-09-09 | Reaffirmed complete-ecosystem scope and user-choice interpretation of “optional”. |
| 2026-09-09 | Reaffirmed shared-infrastructure-first, one-Case, provider-neutral, privacy-first architecture. |
| 2026-09-09 | Deferred broad channel/AI/Web3/hardware expansion until core vertical slice dependencies are verified. |

**Master rule:** Preserve the full ecosystem scope, but execute only the highest-value unresolved dependency frontier. Never mark design as implementation. Never delete history before evidence-backed archival.
