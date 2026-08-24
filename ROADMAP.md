# 🇮🇳 JANAVANI — FULL ECOSYSTEM ROADMAP

**Status:** ACTIVE — ECOSYSTEM BUILD  
**Version:** 2.1  
**Date:** 24 August 2026

> Janavani is being built as a full citizen-governance ecosystem. The roadmap is capability- and architecture-driven, not an MVP completion plan.

## 1. STRATEGIC DESTINATION

```text
Citizen Reality
   ↓
Understanding + Evidence
   ↓
Correct Authority
   ↓
Lawful Civic Action
   ↓
Submission / Communication
   ↓
Government Response
   ↓
Tracking / Follow-up / Escalation
   ↓
Outcome
   ↓
Accountability
   ↓
Public Learning
```

The ecosystem must make this lifecycle increasingly usable across Web/WebApp, Android, iOS, messaging, API and decentralized-capable interfaces.

## 2. ROADMAP PRINCIPLES

- Build the ecosystem, not an MVP.
- Capabilities are primary; interfaces are access surfaces.
- Preserve interface independence.
- Let users choose optional capabilities and access surfaces.
- No optional feature becomes an implicit architectural dependency.
- AI is replaceable infrastructure, not the product identity.
- OCR/CV/SAM/VLM/SLM/LLM/MLM/MoE/LAM/RAG/Agentic AI are distinct model/intelligence families, not one mandatory pipeline.
- Privacy by Design and Privacy by Default.
- Safety by Design and Safety by Default.
- Preserve provenance, consent, user control and truthful delivery states.
- Constitutional/legal framing must remain accurate and source-disciplined.
- Existing working capabilities are foundations, not limits on scope.
- Archive obsolete designs rather than silently deleting history.
- Verify implementation status from GitHub code/tests, not documentation alone.
- Do not repeat completed audits; use the Master Checklist and dated audit records.

## 3. WORKSTREAM A — ECOSYSTEM GOVERNANCE & DOCUMENTATION

**Status: IN PROGRESS**

- Ecosystem identity and charter
- North Star reconciliation
- Constitutional governance principles
- Canonical Source of Truth
- Master Architecture
- Product Landscape
- Capability Registry
- User capability-choice model
- Data contracts
- Permission and consent contracts
- Transport abstraction contracts
- Failure/dependency matrix
- Threat model
- Privacy/safety model
- Test strategy
- Documentation authority and archival policy
- Wiki/project/milestone synchronization with canonical docs

## 4. WORKSTREAM B — SHARED PLATFORM

**Status: IN PROGRESS**

Build and converge reusable platform capabilities across:

- Domain model
- Conversation / interaction layer
- Workflow engine
- State and session management
- Services
- Document composition
- Evidence
- Storage and repositories
- Search and government data
- Privacy and security services
- Identity and consent
- Analytics
- Notification and delivery
- API boundaries
- Capability routing
- Health/failure/degraded-state handling
- Async job/event fabric and recovery

The shared platform must remain independent of Telegram, Web, WhatsApp, Messenger, Android, iOS and DApp presentation layers.

## 5. WORKSTREAM C — DYNAMIC WEB / WEBAPP

**Status: ACTIVE BUILD — FIRST PRODUCT-BUILDING SURFACE**

The Web is a first-class product surface, not a temporary MVP shell and not the platform dependency for other clients.

Target capabilities include:

- Dynamic citizen onboarding
- User-controlled capability selection
- Issue understanding
- Guided civic workflows
- Government information discovery
- Office/authority intelligence
- Document creation
- Evidence handling
- Citizen review and approval
- Submission and delivery
- Case tracking
- Follow-up and escalation
- Citizen history with privacy controls
- Feedback and accountability views
- Governance dashboards where appropriate
- Multilingual and accessibility support
- Optional AI/RAG/SLM/LLM/VLM/OCR/CV and controlled agentic features

### First complete Web vertical slice

`issue → understanding → authority → action/draft → evidence → review → submission/tracking`

This is a construction and verification sequence, not a reduction of ecosystem scope.

## 6. WORKSTREAM D — MOBILE ECOSYSTEM

**Status: PLANNED / ARCHITECTURE TRACK**

### Android

Independent Janavani application consuming shared platform APIs/capabilities.

### iOS

Independent Janavani application consuming shared platform APIs/capabilities.

Potential shared mobile capabilities:

- Identity and consent
- Notifications
- Evidence capture
- Location
- Offline/low-bandwidth workflows
- Case tracking
- Emergency/SOS
- Secure local state
- Optional local AI

## 7. WORKSTREAM E — MESSAGING ECOSYSTEM

**Status: EXISTING FOUNDATION + EXPANSION**

### Telegram Bot / app

Existing working interface; protect from unnecessary refactoring while shared capabilities converge.

### Telegram Mini App

First-class Telegram web surface using shared Janavani capabilities rather than bot-owned business logic.

### WhatsApp

Independent integration adapter.

### Messenger

Independent integration adapter.

Messaging is an access layer, not the platform core.

## 8. WORKSTREAM F — API & INTEGRATION PLATFORM

**Status: IN PROGRESS / EXPANDING**

Build stable APIs and contracts for:

- Web/WebApp
- Mobile
- Messaging adapters
- DApp/Web3 interfaces
- Institutional integrations
- Approved third-party applications

API design exposes capabilities rather than interface-specific workflows.

## 9. WORKSTREAM G — DAPP / WEB3 / DECENTRALIZED CAPABILITIES

**Status: ARCHITECTURE / RESEARCH / SELECTIVE IMPLEMENTATION**

Potential capabilities:

- Citizen-controlled identity/credentials
- Verifiable credentials
- Evidence provenance
- Decentralized records where appropriate
- Community-operated infrastructure
- DApp access
- Alternative storage
- Censorship-resilient communication
- Privacy-enhancing technologies

Blockchain, IPFS, Nostr, Nym, Reticulum and other technologies are tools. Each must have a demonstrated capability-level justification and must not become a mandatory dependency for unrelated workflows.

## 10. WORKSTREAM H — CIVIC DOCUMENT ECOSYSTEM

**Status: FOUNDATION EXISTS / EXPANDING**

Document families:

- Complaint
- Grievance
- RTI
- Representation
- Petition
- Objection
- Appeal
- Follow-up
- Escalation
- Whistleblower
- Other lawful civic communications

## 11. WORKSTREAM I — EVIDENCE & KNOWLEDGE

**Status: PLANNED / FOUNDATION**

- Photo/video/document evidence
- Voice evidence where appropriate
- OCR and document understanding
- Computer Vision
- VLM/SAM-assisted analysis where appropriate
- Evidence metadata
- Provenance
- Verification status
- Citizen correction
- Expert review
- Volunteer review
- Institutional review
- Correction history

## 12. WORKSTREAM J — GOVERNMENT INFORMATION & INTELLIGENCE

**Status: EXPANDING**

- Office directory
- Department directory
- Officer information
- Representative information
- Government schemes
- Public services
- Laws/rules/notifications
- Bills and policy changes
- Local-government information
- Project information
- Budget and expenditure information
- Public-source provenance

## 13. WORKSTREAM K — CITIZEN ACTION LIFECYCLE

**Status: FOUNDATION / EXPANDING**

```text
Case
 ↓
Document / Action
 ↓
Submission
 ↓
Acknowledgement
 ↓
Tracking
 ↓
Follow-up
 ↓
RTI / Appeal / Escalation where appropriate
 ↓
Outcome
 ↓
Feedback
```

## 14. WORKSTREAM L — ACCOUNTABILITY & PUBLIC LEARNING

**Status: ARCHITECTURE / FOUNDATION**

Potential capabilities:

- Office/service feedback
- Officer/service experience reporting
- Representative information
- Response-time and resolution signals
- Government performance intelligence
- Project/commitment tracking
- Public dashboards
- Positive governance recognition
- Source-backed public learning

Citizen reports must remain distinguishable from verified findings.

## 15. WORKSTREAM M — AI / INTELLIGENCE FABRIC

**Status: ARCHITECTURE / FOUNDATION**

Model/intelligence families are independently replaceable capabilities behind contracts:

- OCR
- Computer Vision (CV)
- SAM / segmentation
- VLM
- SLM
- LLM
- MLM
- MoE
- LAM
- RAG
- Agentic AI
- Translation/speech/multimodal services

Requirements:

- Provider/model abstraction
- Local/SLM assessment
- RAG with source provenance
- Knowledge freshness policy
- Structured outputs
- Human approval gates
- Tool permissions
- AI failure fallback
- Evaluation suite
- Prompt/version registry
- Hallucination/error reporting
- Multilingual assistance
- Deterministic/degraded path for critical workflows

AI should reduce bureaucratic burden without creating new uncertainty or becoming the sole source of truth.

## 16. WORKSTREAM N — IDENTITY, PRIVACY & SECURITY

**Status: FOUNDATION / EXPANDING**

- Optional account model
- Anonymous workflows where appropriate
- Consent
- Cross-channel identity linking only with consent
- Role/permission system
- Access auditability
- Data minimization
- Retention controls
- Evidence protection
- Threat model
- Abuse prevention
- Privacy by Design
- Privacy by Default
- Safety by Design
- Safety by Default
- Security testing

## 17. WORKSTREAM O — MULTILINGUAL & ACCESSIBILITY

**Status: ARCHITECTURE**

- English baseline
- Indian-language architecture
- Malayalam and other regional-language support
- Manglish normalization
- Voice where supported
- Accessibility baseline
- Low-bandwidth UX
- Offline-capable workflows where required

## 18. WORKSTREAM P — SOS & RESILIENT TRANSPORT

**Status: ARCHITECTURE LOCKED / IMPLEMENTATION PROGRESSIVELY VERIFIED**

Potential transport layers:

- Internet
- Local Bluetooth/Wi-Fi
- Mesh / Reticulum / LoRa-class transport
- Community relay/gateway
- Satellite-capable transport

Emergency capability requires stronger resilience, integrity, privacy, delivery-state, retry, and abuse controls than ordinary workflows.

## 19. WORKSTREAM Q — EXPERT / VOLUNTEER / NGO / INSTITUTION ECOSYSTEM

**Status: ARCHITECTURE**

- Registration
- Verification levels
- Expertise registry
- Review assignment
- Conflict-of-interest controls
- Reputation/quality safeguards
- Institutional participation
- Permission control

## 20. WORKSTREAM R — OPERATIONS & DEPLOYMENT

**Status: IN PROGRESS**

- Independent runtimes
- Deployment topology
- Configuration management
- CI/CD
- Observability
- Metrics
- Health checks
- Backup/recovery
- Security scanning
- Dependency management
- Release evidence
- Failure-injection testing
- Queue/DLQ observability

## 21. WORKSTREAM S — VERIFICATION & QUALITY

**Status: CONTINUOUS**

Every capability progresses through:

```text
VISION
 ↓
DESIGNED
 ↓
IMPLEMENTED
 ↓
FUNCTIONAL
 ↓
TESTED
 ↓
SECURITY-VERIFIED
 ↓
PRIVACY-VERIFIED
 ↓
PRODUCTION-READY
```

The Master Task Checklist is the control mechanism for this progression.

## 22. CURRENT SEQUENCE

The immediate sequence is not “finish MVP, then ecosystem.”

It is:

1. **Canonical documentation + constitutional governance convergence**
2. **Capability registry, dependency matrix and contracts**
3. **Shared-platform/runtime convergence**
4. **Dynamic Web/WebApp foundation and first complete vertical slice**
5. **Expand and verify civic capabilities**
6. **API and integration platform**
7. **Telegram Mini App / WhatsApp / Messenger integrations**
8. **Android and iOS applications**
9. **DApp/Web3 capabilities where justified**
10. **AI/intelligence fabric expansion and model independence**
11. **Governance intelligence, accountability and public-learning layers**
12. **Resilient/decentralized transport and advanced ecosystem capabilities**

These streams can overlap when dependencies and verification permit.

## 23. DEFINITION OF SUCCESS

Janavani succeeds when citizens can use one coherent ecosystem across multiple independent interfaces to move from lived public problems to informed action, institutional response, follow-up, accountability and public learning — while preserving privacy, safety, provenance, user control, constitutional/legal discipline and system resilience.

**The target is the ecosystem.**
