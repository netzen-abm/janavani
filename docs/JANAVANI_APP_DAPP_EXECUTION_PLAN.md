# 🇮🇳 JANAVANI — APP + DAPP EXECUTION PLAN

**Status:** ACTIVE — CURRENT EXECUTION CONTROL
**Version:** 1.0
**Date:** 24 August 2026

## 1. Purpose

This document establishes the immediate engineering execution priority for Janavani while preserving the full ecosystem scope.

**Immediate product priority:** Android + iOS + DApp.

This is an execution priority, not a reduction of ecosystem scope. Dynamic Web/WebApp, Telegram, Telegram Mini App, WhatsApp, Messenger, API, decentralized transports, AI/intelligence families and future protocol integrations remain first-class ecosystem capabilities and must remain architecturally independent.

If another canonical document says that Dynamic Web is the first active product-building surface, this execution plan supersedes that sequencing statement for the current implementation phase. The Dynamic Web remains an active parallel surface, but App + DApp are now the primary product construction focus.

## 2. Non-negotiable architecture

```text
                         JANAVANI ECOSYSTEM
                                │
                    Shared Capability Contracts
                                │
          ┌─────────────────────┼─────────────────────┐
          │                     │                     │
       Android                  iOS                  DApp
          │                     │                     │
          └──────────────┬──────┴──────┬──────────────┘
                         │             │
                    Independent    Independent
                    client shell   client shell
                         │             │
                         └──────┬──────┘
                                │
                    Janavani Platform Contracts
                                │
       ┌────────────────────────┼────────────────────────┐
       │                        │                        │
   Domain/Workflow         Data/Trust              Adapters
       │                        │                        │
       └────────────────────────┼────────────────────────┘
                                │
      Internet / Nostr / Nym / Reticulum / Freenet / Web3
```

### Independence rules

1. Android must work without iOS, Web, Telegram, WhatsApp, Messenger or DApp.
2. iOS must work without Android, Web, Telegram, WhatsApp, Messenger or DApp.
3. DApp must work without Android, iOS, Telegram or messaging surfaces.
4. Web/WebApp remains independently deployable.
5. Telegram/Mini App/WhatsApp/Messenger remain adapter surfaces and never own domain logic.
6. AI is optional. Non-AI workflows must remain usable when AI is unavailable.
7. Blockchain/Web3 is optional. Ordinary civic workflows must remain usable when blockchain is unavailable.
8. Nostr, Nym, Reticulum and Freenet are optional transport/storage/privacy capabilities; none is a universal dependency.
9. A provider outage must produce a truthful degraded state rather than break unrelated capabilities.
10. A user chooses which available surfaces and capabilities to enable, subject to explicit legal, safety, destination, device and technical constraints.

## 3. Privacy and administrator boundary

Janavani is privacy-first by design and by default.

- Personal data should remain on the user's device whenever the capability does not require remote processing.
- Data that must leave the device must be minimised, encrypted in transit and protected according to its sensitivity and purpose.
- Backend administrators must not have routine access to sensitive user content.
- Server-side operational metadata must be separated from user content wherever technically possible.
- Keys required to decrypt private user content should remain under user/device control wherever the capability permits.
- Remote processing must be explicit and capability-specific.
- Local/offline processing should be preferred for sensitive OCR, document analysis, evidence preparation and AI where practical.
- Logs, telemetry and diagnostics must not become an accidental personal-data collection channel.
- Emergency and high-risk workflows require stronger metadata minimisation and access controls.

## 4. App + DApp vertical slice

The first complete product slice should prove the architecture through a useful citizen workflow rather than through a collection of disconnected screens.

```text
Install / Open
    ↓
Privacy + Capability Choice
    ↓
Local Secure Profile / Guest Mode
    ↓
Create Civic Case
    ↓
Describe Problem
    ↓
Evidence Capture / Import
    ↓
Authority & Destination Resolution
    ↓
Draft Complaint / Grievance / RTI / Representation
    ↓
User Review + Corrections
    ↓
Choose Submission Channel
    ↓
Submit or Save Locally
    ↓
Truthful Delivery State
    ↓
Track / Follow-up / Escalate
```

Every step must have a non-AI and degraded path where technically practical.

## 5. First capability contracts

### APP-CORE-001 — Capability Manager

Users can see available capabilities and independently enable/disable optional capabilities.

Required properties:

- capability ID
- status
- permissions
- dependencies
- privacy impact
- local/remote processing declaration
- available interfaces
- failure/degraded behavior

### APP-CORE-002 — Secure Local State

Local-first storage for drafts, case state, user preferences, capability settings and private evidence.

Required properties:

- encryption at rest
- key ownership model
- explicit export/delete controls
- migration/versioning
- recovery policy
- no silent cloud replication

### APP-CIVIC-001 — Civic Case

A case is a portable domain object independent of any interface or transport.

Minimum conceptual state:

`DRAFT → REVIEW → READY → SUBMITTING → SUBMITTED/QUEUED → ACKNOWLEDGED → FOLLOW_UP → RESOLVED/CLOSED`

No client may equate `SUBMITTING` or `SENT` with government acknowledgement.

### APP-EVIDENCE-001 — Evidence Bundle

Evidence is captured and maintained independently of AI.

Supported classes may include documents, photographs, audio, video, structured facts and source references.

Required metadata:

- source
- capture time where available
- transformation history
- integrity/hash metadata where appropriate
- user consent
- verification status

### APP-AUTH-001 — Authority Resolution

Resolve the intended department/office/authority using versioned and provenance-backed records.

Citizen corrections are proposals, not automatic truth. Corrections require verification before becoming authoritative.

### APP-DOC-001 — Civic Document Generation

Generate purpose-bound complaint, grievance, RTI, petition, objection, representation, appeal and follow-up documents.

Outputs:

- editable structured document
- PDF
- DOCX where supported
- verified To/CC postal and email destinations where available
- source/provenance information

### APP-SUB-001 — Submission Router

Submission must be transport-independent.

```text
Case
 ↓
Submission Package
 ↓
Destination Adapter
 ├─ Internet/API
 ├─ Email
 ├─ Government portal
 ├─ Messaging adapter
 ├─ Nostr
 ├─ Nym
 ├─ Reticulum
 ├─ Freenet
 └─ Future adapter
```

Each adapter reports its own delivery state.

### APP-TRACK-001 — Case Tracking

Track acknowledgements, references, responses, deadlines, follow-ups and escalation history without requiring a specific transport.

### DAPP-001 — Optional Web3 Layer

The DApp may provide user-controlled credentials, verifiable records, evidence hashes, decentralized provenance or other justified capabilities.

It must not require blockchain availability for ordinary civic cases.

## 6. AI capability isolation

The AI fabric is a set of replaceable services, not one pipeline:

```text
OCR ───────┐
CV ────────┤
SAM ───────┤
VLM ───────┤
SLM ───────┤
LLM ───────┤
MLM ───────┤→ AI Capability Contract → Workflow
MoE ───────┤
LAM ───────┤
RAG ───────┤
Agentic AI ┘
```

Rules:

- OCR failure does not disable manual document entry.
- RAG failure never causes fabricated source claims.
- LLM failure may fall back to SLM or deterministic workflows where appropriate.
- Agent failure leaves a guided workflow.
- Vision-model failure leaves manual evidence review.
- AI output is clearly labelled and remains subject to user review.
- Consequential external actions require explicit user approval.

## 7. Transport and decentralized capability isolation

The client must interact with a transport abstraction rather than hard-code a network technology.

Required initial states:

`AVAILABLE`, `DEGRADED`, `UNAVAILABLE`, `NOT_CONFIGURED`.

The system must support future adapters without redesigning civic domain objects. Initial ecosystem references include Internet, Nostr, Nym Mixnet, Reticulum, Freenet and blockchain/Web3 capabilities. Future Web4/Web5/Web6-class technologies can be added through new adapters/contracts rather than modifying core civic workflows.

## 8. Build sequence

### Phase A — Contracts and shell

- capability registry binding for App/DApp
- client capability manager
- secure local state contract
- platform-neutral case model
- evidence bundle model
- submission/delivery state machine
- transport abstraction
- privacy/permission model

### Phase B — Android foundation

- native application shell
- local encrypted state
- capability selection
- civic case creation
- evidence capture/import
- document preview/export
- network/degraded state
- notification abstraction

### Phase C — iOS foundation

Implement the same capability contracts independently. Do not copy Android-specific runtime assumptions into the platform contract.

### Phase D — DApp foundation

- wallet-independent guest capability where possible
- optional Web3 identity/credential integration
- verifiable evidence/provenance options
- capability selection
- civic case access through shared contracts
- blockchain failure isolation

### Phase E — First complete civic workflow

Deliver and test:

`problem → evidence → authority → document → review → submission → acknowledgement/tracking → follow-up`

### Phase F — Ecosystem adapters

In parallel, progressively connect Web/WebApp, Telegram/Mini App, WhatsApp, Messenger, API, Nostr, Nym, Reticulum and Freenet through independent adapters.

## 9. Verification gates

A feature is not considered complete because its screen exists.

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
FAILURE-ISOLATION-VERIFIED
 ↓
PRODUCTION-READY
```

For App/DApp, verification must include at least:

- unit tests
- integration tests
- offline/degraded tests
- provider-failure tests
- permission tests
- local-storage encryption tests
- sensitive-data exposure tests
- transport independence tests
- AI-disabled tests
- blockchain-disabled tests
- user-review/approval tests
- truthful delivery-state tests

## 10. Definition of done for the first App/DApp milestone

The milestone is complete only when a citizen can independently use Android, iOS and DApp to create and manage a civic case without requiring another interface to be online, while optional AI/Web3/decentralized capabilities can be enabled or disabled independently.

The milestone must also demonstrate that:

- private data remains under the declared privacy boundary;
- administrators cannot routinely inspect sensitive user content;
- a failed optional subsystem does not stop unrelated workflows;
- no submission is reported as successful without appropriate acknowledgement;
- source/provenance and user-generated claims remain distinguishable;
- the same domain case is portable across supported interfaces without making one interface the owner of the case.

## 11. Full ecosystem remains active

This plan does not retire or postpone the ecosystem capabilities already defined in the canonical registry, including:

- dynamic Web/WebApp
- Telegram and Telegram Mini App
- WhatsApp
- Messenger
- public/partner APIs
- Nostr
- Nym Mixnet
- Reticulum
- Freenet
- blockchain/ZKP/Web3
- OCR/CV/SAM/VLM/SLM/LLM/MLM/MoE/LAM/RAG/Agentic AI
- government schemes/events/information
- bills/Acts/ordinances and constitutional analysis
- citizen opinions/objections
- complaints/grievances/RTI/BSA workflows
- office/officer/representative/service accountability
- escalation and remedy workflows
- government claim/performance verification
- financial contribution and expenditure transparency
- expert/volunteer/NGO/institution participation
- SOS and resilient transport

The execution rule is **App/DApp first while the ecosystem contracts continue to evolve in parallel**.

## 12. Repository control

Every implementation task should link back to:

1. this execution plan;
2. `docs/SOURCE_OF_TRUTH.md`;
3. `docs/CAPABILITY_REGISTRY.md`;
4. `docs/MASTER_TASK_CHECKLIST.md`;
5. `ROADMAP.md`;
6. the actual code/tests proving the status.

Do not create duplicate capability implementations merely because a new interface is being built. Add an adapter or contract implementation instead.

## 13. Engineering opinion

The most important design decision is **not to make the App the new monolith**. The App should be the first high-quality citizen client of the ecosystem.

The reusable unit should be the capability contract and domain state, while Android, iOS, DApp, Web and messaging remain replaceable access surfaces. This gives Janavani a practical path from today's App/DApp focus to a much larger ecosystem without repeatedly rewriting business logic.
