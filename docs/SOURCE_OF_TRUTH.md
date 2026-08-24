# JANAVANI — CANONICAL SOURCE OF TRUTH

**Status:** LOCKED — CURRENT ARCHITECTURAL REFERENCE  
**Version:** 2.2  
**Date:** 24 August 2026  
**Repository:** `netzen-abm/janavani`

## 1. IDENTITY

Janavani is a **full citizen-governance ecosystem**. It is not a Telegram bot, not a single application, and not an MVP whose scope ends at complaint/PDF generation.

The ecosystem operates within India's constitutional and legal environment and is citizen-centered. The Preamble's **"We, the People of India"** framing is a core civic principle. Articles **14, 19 and 21** form a relevant constitutional framework for equality, freedoms, life, personal liberty and privacy-sensitive design where applicable. **Article 51A** contains citizens' Fundamental Duties and may inform civic participation/education; it is not a standalone authorization for Janavani to exercise public authority. The **Bharatiya Sakshya Adhiniyam (BSA)** is statutory evidence law, not constitutional text.

Janavani is not a court, government authority, election authority, law-enforcement body, or substitute for qualified legal representation.

## 2. USER CHOICE

Janavani is capability-first and user-controlled.

Users may choose among available access surfaces and optional capabilities, including Web/WebApp, Android, iOS, Telegram, Telegram Mini App, WhatsApp, Messenger, API, DApp/Web3, local/offline and resilience features, and optional AI/agentic functions.

Optional capabilities must not silently become mandatory dependencies. Safety, legal, destination, device, network and emergency constraints may limit choices and must be explicit.

## 3. CORE ARCHITECTURE

```text
Citizen / External Actor
          ↓
Independent Interface / Integration
          ↓
Shared Janavani Platform Contracts
          ↓
Domain + Workflow + Reusable Capabilities
          ↓
Data + Trust + Provenance
          ↓
External Government / Civic Systems
```

Capabilities are primary. Interfaces are access surfaces. Implementations are replaceable behind contracts.

## 4. INTERFACE INDEPENDENCE

No interface owns shared business logic and no interface should normally depend on another interface.

```text
Web / WebApp ───────┐
Telegram ───────────┤
Mini App ───────────┤
WhatsApp ───────────┤
Messenger ──────────┤
Android ────────────┤→ JANAVANI PLATFORM
 iOS ───────────────┤
DApp ───────────────┤
API ────────────────┘
```

## 5. RUNTIME AND FAILURE INDEPENDENCE

Each interface/capability must have an explicit runtime boundary appropriate to its role. An interface must not start another interface as part of normal operation.

Failures must be isolated:

- Web outage must not disable Telegram/mobile/API.
- Telegram outage must not disable Web/mobile/API.
- AI provider/model failure must not break non-AI workflows.
- RAG failure must degrade truthfully rather than trigger hallucinated content.
- OCR/CV/VLM/SAM failure must not eliminate manual evidence paths where practical.
- Agent runtime failure must leave a guided deterministic path where practical.
- Blockchain/decentralized-network failure must not break ordinary civic or SOS operation.
- Mesh/satellite failure must never be reported as successful delivery.
- Storage/provider failure must have an explicit recovery/degraded policy.

## 6. SHARED PLATFORM LAYERS

Current repository layers include:

- `src/conversation/` — interaction, state, session, routing
- `src/workflow/` — reusable workflow steps
- `src/engine/` — workflow/state execution
- `src/domain/` — citizen, issue, office, location, document, evidence, remedy, submission
- `src/services/` — shared application/business capabilities
- `src/documents/` — composition, standards, delivery, PDF
- `src/storage/` — persistence, repositories, cache, Supabase integration
- `src/models/` — application models
- `src/core/` — configuration and shared core services
- `src/adapters/` — external interface adapters
- `src/web/` — Web interface and API assembly

These are implementation locations, not reasons for cosmetic restructuring.

## 7. CANONICAL API ASSEMBLY BOUNDARY

`src/web/canonical_app.py` is the current **canonical API assembly boundary** established by the M3-D architectural convergence work. It assembles approved domain routers into the shared API surface without importing the historical `src.web.app` application.

This does **not** by itself establish the production runtime entry point. Production runtime ownership remains a verification task until deployment configuration, process startup, imports, health behavior and end-to-end execution have been verified.

Therefore:

```text
Canonical API assembly ≠ Canonical production runtime
```

Historical/transition entry points must not be deleted solely because `canonical_app.py` exists. Runtime/deployment dependency must be verified first.

## 8. CAPABILITY FAMILIES

Janavani progressively provides identity/consent/user control; issue understanding; government authority intelligence; civic documents; evidence/provenance; submission and tracking; follow-up/RTI/appeal/escalation; schemes/benefits; law/bill/notification/policy intelligence; corrections; accountability; government performance/financial transparency; expert/volunteer/NGO/institution participation; multilingual/accessibility; OCR/vision/document understanding; AI/RAG/SLM/LLM/MLM/MoE/VLM/LAM/SAM and controlled Agentic AI; analytics/public learning; SOS/resilient transport; and DApp/Web3/decentralized capabilities where justified.

## 9. AI / MODEL TAXONOMY

AI is optional, purpose-bound and replaceable. Model families are implementations, not the product identity:

- **OCR** — optical character recognition.
- **Computer Vision (CV)** — visual detection/classification/analysis.
- **SAM** — segmentation/object-mask models.
- **VLM** — vision-language models.
- **SLM** — small/local language models.
- **LLM** — large language models.
- **MLM** — masked-language-model family where appropriate.
- **MoE** — mixture-of-experts architecture.
- **LAM** — language-action model family.
- **RAG** — retrieval-augmented generation with source grounding.
- **Agentic AI** — controlled tool-using workflows with explicit permissions and approval gates.

A capability may use zero, one, or multiple model families. No model/provider is a mandatory single point of failure for unrelated capabilities.

## 10. DATA, PROVENANCE AND AUTHORITY

Where information affects citizen action, Janavani should preserve provenance and distinguish source classes. Prefer authoritative/primary sources and versioned records.

A citizen report is not automatically a verified factual finding. AI-generated material is not an official government determination. Delivery attempts are not acknowledgements.

## 11. PRIVACY AND SAFETY

**Privacy by Design, Privacy by Default, Safety by Design and Safety by Default are ecosystem invariants.**

Requirements include minimum necessary collection, purpose limitation, consent, identity minimization, user control, access control, secure evidence handling, retention controls, auditability, threat modelling, abuse prevention and secure recovery behavior.

## 12. DYNAMIC WEB

The Dynamic Web is the first active product-building surface and a first-class product surface. It must be independent of Telegram and must progressively expose shared capabilities: citizen workflows, government information, documents, evidence, tracking, feedback, governance intelligence, multilingual/accessibility and appropriate public views.

The Web is a construction priority, not the ecosystem boundary or a dependency for other interfaces.

## 13. MOBILE

Android and iOS are first-class independent interfaces. They consume shared platform capabilities and do not depend on Telegram, Web, WhatsApp or Messenger for core operation.

## 14. TELEGRAM / MINI APP / MESSAGING

Telegram Bot, Telegram Mini App, WhatsApp and Messenger are independent access surfaces connected through adapters. None may own shared business logic or become a required dependency for another channel.

## 15. API / DAPP / WEB3

APIs expose reusable platform capabilities to approved consumers. DApp/Web3 capabilities may provide decentralized identity, verifiable records, evidence provenance, citizen-controlled credentials, community infrastructure or other justified functions.

Blockchain, IPFS, Nostr, Nym, Reticulum and other technologies are tools, not mandatory dependencies.

## 16. FULL CITIZEN-GOVERNANCE LIFECYCLE

```text
Citizen Reality
 ↓
Understanding
 ↓
Evidence / Context
 ↓
Correct Authority
 ↓
Lawful Civic Action
 ↓
Submission / Communication
 ↓
Government Response
 ↓
Tracking
 ↓
Follow-up / RTI / Escalation
 ↓
Outcome
 ↓
Feedback / Accountability
 ↓
Public Learning
```

## 17. STATUS DISCIPLINE

Use explicit capability states:

`VISION` → `DESIGNED` → `IMPLEMENTED` → `FUNCTIONAL` → `TESTED` → `SECURITY-VERIFIED` → `PRIVACY-VERIFIED` → `PRODUCTION-READY`

Code or documentation alone does not establish completion.

## 18. CHANGE RULE

Before changing code:

1. Check North Star, Ecosystem Charter, Constitutional Governance and this Source of Truth.
2. Check Master Architecture, Product Landscape and Roadmap.
3. Check Capability Registry and Master Checklist/subtasks.
4. Inspect actual GitHub implementation, imports, tests and deployment references.
5. Avoid duplicate implementations.
6. Make a small justified change.
7. Test and verify.
8. Record evidence.
9. Update affected documentation.

## 19. ARCHIVE RULE

Historical/superseded documents should be archived rather than allowed to compete with active direction. Code is removed only after replacement, dependency/import verification, tests, runtime verification and documentation reconciliation.

## 20. CURRENT EXECUTION PHASE

The current phase is **ecosystem foundation convergence + Dynamic Web active build + runtime verification**. The full ecosystem remains the destination. Current engineering tasks are construction and verification units inside that ecosystem, not product-scope reductions.

## 21. FINAL RULE

**Build Janavani as one coherent ecosystem with many independent interfaces and shared capabilities. Let citizens choose the capabilities and surfaces they need. Preserve constitutional/legal discipline, privacy, safety, provenance, user control and failure isolation by design and by default.**
