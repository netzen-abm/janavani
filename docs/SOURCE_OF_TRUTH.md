# JANAVANI — CANONICAL SOURCE OF TRUTH

**Status:** LOCKED — CURRENT ARCHITECTURAL REFERENCE
**Version:** 2.0
**Date:** 23 August 2026
**Repository:** `netzen-abm/janavani`

## 1. IDENTITY

Janavani is a **full citizen-governance ecosystem**. It is not a Telegram bot, not a single application, and not an MVP whose scope ends at complaint/PDF generation.

Existing working capabilities are foundations within the larger ecosystem.

The intended independent access surfaces are:

- Dynamic Web
- Android
- iOS
- Telegram Bot
- Telegram Mini App
- WhatsApp
- Messenger
- API
- DApp / Web3 capabilities
- Decentralized/resilient transports where justified

## 2. CORE ARCHITECTURE

```text
Citizen / External Actor
          ↓
Independent Interface / Integration
          ↓
Shared Janavani Platform
          ↓
Reusable Capabilities
          ↓
Domain + Workflow + Services + Data + Trust
          ↓
External Government / Civic Systems
```

Capabilities are primary. Interfaces are access surfaces.

## 3. INTERFACE INDEPENDENCE

No interface owns shared business logic and no interface should normally depend on another interface.

```text
Web        ─┐
Telegram   ─┤
Mini App   ─┤
WhatsApp   ─┤
Messenger  ─┤
Android    ─┤→ JANAVANI PLATFORM
 iOS       ─┤
DApp       ─┤
API        ─┘
```

## 4. RUNTIME INDEPENDENCE

Each interface/deployment must have an explicit runtime boundary appropriate to its role. An interface must not start another interface as part of normal operation.

Runtime ownership must be verified against actual deployment configuration before legacy entry points are removed.

## 5. SHARED PLATFORM LAYERS

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
- `src/web/` — Web interface/API assembly

These are implementation locations, not reasons for cosmetic restructuring.

## 6. CAPABILITY FAMILIES

Janavani is expected to progressively provide:

- Identity, consent, permissions and user control
- Issue understanding and classification
- Government office/authority intelligence
- Civic document composition
- Evidence and provenance
- Submission, delivery and tracking
- Follow-up, RTI, appeal and escalation
- Government schemes and benefits intelligence
- Policy/law/bill/notification intelligence
- Citizen feedback and corrections
- Office/service/representative accountability
- Government performance and financial-transparency intelligence
- Expert/volunteer/NGO/institution participation
- Multilingual/accessibility services
- AI/RAG/SLM/LLM assistance
- Analytics and public learning
- Emergency/SOS and resilient transport
- DApp/Web3/decentralized capabilities where justified

## 7. AI INDEPENDENCE

AI is optional and replaceable infrastructure. Defined workflows must have appropriate non-AI fallback behavior.

AI must distinguish citizen facts, authoritative verified information, system-derived information, AI suggestions and unverified information.

AI must not fabricate legal facts, authorities, evidence, dates, events or government actions.

## 8. DATA AND PROVENANCE

Where information affects citizen action, Janavani should preserve provenance and distinguish source classes. Authoritative/primary sources and verified structured data are preferred.

A citizen report is not automatically a verified factual finding.

## 9. PRIVACY AND SECURITY

Privacy by Design and Privacy by Default are ecosystem invariants.

Requirements include minimum necessary collection, consent, identity minimization, access control, secure evidence handling, retention controls, auditability, threat modelling, abuse prevention and secure recovery behavior.

## 10. DYNAMIC WEB

The Web is a first-class product surface. It must be independent of Telegram and progressively expose the broader ecosystem: citizen workflows, government information, documents, evidence, tracking, feedback, governance intelligence, multilingual/accessibility features and public views where appropriate.

## 11. MOBILE

Android and iOS are first-class independent interfaces. They consume shared platform capabilities and do not depend on Telegram, Web, WhatsApp or Messenger for core operation.

## 12. TELEGRAM / MINI APP

Telegram is an existing working interface and an important foundation. It is not the platform. The Telegram Bot and Telegram Mini App must consume shared capabilities.

The existing working bot flow should be protected from unnecessary refactoring while platform convergence proceeds.

## 13. WHATSAPP / MESSENGER

Both are independent integrations connected through adapters/integration boundaries. Neither may own shared business logic.

## 14. API / DAPP / WEB3

APIs expose reusable platform capabilities to approved consumers. DApp/Web3 capabilities may provide decentralized identity, verifiable records, evidence provenance, citizen-controlled credentials, community infrastructure or other justified functions.

Blockchain, IPFS, Nostr, Nym, Reticulum and other technologies are tools, not mandatory dependencies.

## 15. FULL CITIZEN-GOVERNANCE LIFECYCLE

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

## 16. STATUS DISCIPLINE

Use explicit capability states:

`VISION` → `DESIGNED` → `IMPLEMENTED` → `FUNCTIONAL` → `TESTED` → `SECURITY-VERIFIED` → `PRIVACY-VERIFIED` → `PRODUCTION-READY`

Code or documentation alone does not establish completion.

## 17. CHANGE RULE

Before changing code:

1. Check Ecosystem Charter, North Star and this Source of Truth.
2. Check Master Architecture, Product Landscape and Roadmap.
3. Check Capability Registry and Master Checklist/subtasks.
4. Inspect actual GitHub implementation, imports, tests and deployment references.
5. Avoid duplicate implementations.
6. Make a small justified change.
7. Test and verify.
8. Record evidence.
9. Update affected documentation.

## 18. ARCHIVE RULE

Historical/superseded documents should be archived rather than allowed to compete with active direction. Code is removed only after replacement, dependency/import verification, tests, runtime verification and documentation reconciliation.

## 19. FINAL RULE

**Build Janavani as one coherent ecosystem with many independent interfaces and shared capabilities. Never reduce the project to an MVP, a Telegram bot, or a single web application.**
