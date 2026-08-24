# 🇮🇳 JANAVANI — APP + DAPP ECOSYSTEM ACTION PLAN

**Status:** ACTIVE — CONTROL DOCUMENT  
**Date:** 24 August 2026  
**Purpose:** Prevent loss of architectural decisions while implementing the first product surfaces.

## 1. Locked direction

Janavani is a **full citizen-governance ecosystem**. The first implementation focus is **Android + iOS App and DApp/Web3**, while Dynamic Web/WebApp remains a first-class independent product surface. This ordering does not create an MVP and does not reduce the ecosystem scope.

Every interface and major capability must be independently operable wherever technically possible. No interface is the dependency of another interface.

## 2. Frontend architecture decision

```text
                 [ JANAVANI FRONTEND CLIENT ]
                    /          |           \
                   /           |            \
             Identity      Network Layer    Data & State Verification
                /               |                    \
             Nostr           Nym Mixnet        Blockchain / ZKP
                                |
                         Reticulum Mesh
                                |
                         Freenet (research)
                                |
                    Offline / Store-and-Forward
```

### Identity

Nostr is an optional decentralized identity/event mechanism. It does not replace all Janavani identity modes. Anonymous, account-based and other capability-specific identity modes remain possible.

### Network/privacy

Nym Mixnet is an optional privacy-enhancing transport. Reticulum is an optional resilient/mesh transport. Direct Internet, local/offline and other approved transports remain available.

### Verification/state

Blockchain and ZKP are optional verification/provenance mechanisms. They are not the mandatory application database or civic workflow runtime.

### Freenet

Freenet is a research/integration track for decentralized/distributed storage or communication. Production use requires a separate capability contract, threat model, performance review, privacy review, legal review and failure-mode verification.

## 3. Product independence matrix

| Surface | Must operate independently | Can consume shared contracts | Must not depend on |
|---|---|---|---|
| Android | Yes | Yes | iOS/Web/DApp |
| iOS | Yes | Yes | Android/Web/DApp |
| DApp | Yes | Yes | Mobile/Web |
| Dynamic Web/WebApp | Yes | Yes | Mobile/DApp |
| Telegram | Yes | Yes | Web |
| Telegram Mini App | Yes | Yes | Telegram bot business logic |
| WhatsApp | Yes | Yes | Telegram/Web |
| Messenger | Yes | Yes | Telegram/Web |
| API | Yes | Yes | Any presentation surface |

## 4. First App vertical slice

```text
Onboard
  ↓
Choose capabilities
  ↓
Describe civic issue
  ↓
Understand / classify
  ↓
Identify authority
  ↓
Choose lawful action
  ↓
Capture / attach evidence
  ↓
Generate / prepare document
  ↓
Citizen review
  ↓
Explicit approval
  ↓
Submit
  ↓
Track acknowledgement and response
  ↓
Follow-up / escalation
```

The workflow must have a deterministic/manual path. AI improves the experience but never owns the civic workflow.

## 5. First DApp vertical slice

```text
Enter without wallet where possible
  ↓
Choose a Web3 capability
  ↓
Inspect credential / provenance / evidence state
  ↓
Understand network and transaction implications
  ↓
Explicit user confirmation
  ↓
Optional decentralized action
  ↓
Verify resulting state
  ↓
Return to ordinary civic case lifecycle
```

No silent wallet connection and no silent transaction signing.

## 6. Core capability backlog

### Citizen action

- Complaint generation
- Grievance petition
- RTI generation
- Representation
- Petition
- Appeal/follow-up
- Escalation
- Policy opinion
- Objection
- Whistleblower workflow where legally appropriate

### Government information

- Central/state/local schemes
- Online/offline government events
- Public services
- Office/department directory
- Officer information
- Elected representative information
- Bills
- Acts
- Ordinances
- Rules/notifications/circulars
- Projects and commitments
- Budget/expenditure information where authoritative data exists

### Legislation and policy intelligence

For each tracked bill/act/ordinance/policy item:

1. ingest authoritative source;
2. maintain version/status history;
3. provide plain-language summary;
4. identify affected areas;
5. retrieve relevant constitutional/statutory sources;
6. evaluate selected provisions against the applicable constitutional/legal framework;
7. highlight potential concerns with calibrated confidence;
8. provide citations/source provenance;
9. allow citizen opinion/objection;
10. generate the appropriate communication;
11. verify recipients;
12. export PDF/DOCX;
13. track submission/response.

Automated analysis is not a judicial determination.

### Accountability

- Service ratings
- Office reviews
- Officer experience/review
- Department performance signals
- Bureaucratic service experience reporting
- MP/MLA/representative information and public-service signals
- Government claim verification
- Project/commitment tracking
- Positive recognition for good service
- Corrective grievance and escalation

A rating is a user-experience signal, not a finding of corruption or misconduct. Serious allegations require evidence, provenance, fair-process safeguards, correction and lawful escalation.

### Escalation

A supported unresolved matter may progress through an appropriate chain such as:

`service/office → responsible authority → department head → administrative/grievance authority → relevant elected representative where appropriate`

The actual route must be determined from the applicable jurisdiction and authority data; Janavani must not invent escalation destinations.

## 7. Document engine requirements

The document engine must support:

- complaint;
- grievance petition;
- RTI;
- representation;
- petition;
- policy opinion;
- objection;
- appeal;
- follow-up;
- escalation;
- approved whistleblower submissions;
- emergency reports.

Output:

- PDF
- DOCX
- printable document
- structured machine-readable representation where useful

Recipient records must support:

- name/designation;
- office/department;
- postal address;
- email;
- source;
- verification status;
- last verified time where available.

CC recipients must be explicit and workflow-justified.

## 8. Address correction and verification

Users can report an incorrect recipient address/email.

Correction flow:

`current record → proposed correction → evidence/source → verification → review → canonical update → correction history`

The original value must not disappear without history. A user-submitted correction is not automatically authoritative.

## 9. Financial contribution engine

Financial contributions are a separate high-assurance capability.

The engine must expose, before payment:

- recipient legal identity/status;
- purpose;
- amount;
- fees;
- payment route;
- restrictions;
- refund rules;
- tax/receipt information where applicable;
- conflict-of-interest information where applicable.

After payment it must expose:

- transaction/receipt ID;
- payment state;
- settlement state;
- reconciliation state;
- allocation category where applicable;
- transparent reporting.

The system should support auditable periodic reports and appropriate public transparency without exposing donors' personal information by default.

**Important boundary:** contributions must never buy preferential treatment, government influence, officer ratings, case priority, or official decisions. Personal payments to officers are not a Janavani contribution capability.

Blockchain can optionally strengthen provenance, but it does not replace accounting, audit, statutory compliance or financial controls.

## 10. Government information freshness

Every government-information item should carry:

`SOURCE → ISSUER → JURISDICTION → VERSION/STATUS → LAST CHECKED → VERIFICATION STATE`

Stale or unavailable information must be represented as stale/unavailable rather than silently presented as current.

## 11. AI architecture

AI families remain separate, replaceable capabilities:

- OCR
- Computer Vision
- SAM
- VLM
- SLM
- LLM
- MLM
- MoE
- RAG
- LAM
- Agentic AI
- translation/speech/multimodal services

Routing is capability-specific and may consider:

- user choice;
- privacy mode;
- device capability;
- latency;
- cost;
- model availability;
- source requirements;
- safety policy.

Critical workflows require deterministic/manual fallbacks.

## 12. Failure-isolation requirements

The following must be testable:

- Android unavailable → iOS/DApp/Web/API remain usable.
- iOS unavailable → Android/DApp/Web/API remain usable.
- DApp unavailable → ordinary App/Web workflows remain usable.
- Web unavailable → App/DApp/other approved interfaces remain usable.
- Nostr unavailable → other identity modes remain usable.
- Nym unavailable → approved alternate transport remains available.
- Reticulum unavailable → other transport remains available.
- Freenet unavailable → ordinary storage/workflows remain available.
- Blockchain unavailable → ordinary civic workflows remain available.
- ZKP unavailable → non-ZKP capability path remains available where appropriate.
- AI unavailable → deterministic/manual path remains available.
- RAG unavailable → source-unavailable state, never fabricated answer.
- OCR/CV/VLM unavailable → manual evidence path remains available.
- Messaging provider unavailable → case state remains intact.

## 13. Privacy and safety invariants

- Privacy by Design
- Privacy by Default
- Safety by Design
- Safety by Default
- data minimisation
- purpose limitation
- explicit consent where required
- user-controlled identity linking
- no silent wallet connection
- no silent signing
- human approval for consequential external actions
- evidence protection
- provenance
- correction mechanisms
- retention controls
- abuse prevention
- truthful delivery state

## 14. Human flourishing / systems-design research input

The external material supplied for review describes Human Flourishing Architecture as an alignment of individual, social and institutional layers, and presents governance as an adaptive, participatory system. It also describes Project India as a governance ecosystem connecting citizen participation, constitutional literacy, adaptive governance and AI-enabled public systems. These ideas are useful as **design inspiration**, not as legal authority or Janavani requirements by themselves. citeturn0search0turn0view0

Useful design implications for Janavani:

- measure outcomes and human impact, not only activity volume;
- create continuous citizen feedback loops;
- treat governance as an adaptive system with learning and correction;
- connect civic literacy, participation, evidence and institutional response;
- make trust, transparency and participation explicit system properties.

These ideas align with Janavani's existing capability-first and accountability architecture, but they must remain clearly distinguished from India's constitutional/statutory sources.

## 15. Implementation sequence

### Phase A — APP-01 foundation

- Android workspace
- iOS workspace
- DApp workspace
- shared API/capability contracts
- dependency isolation tests
- secure local state boundary
- wallet/no-wallet boundary
- transport abstraction
- capability health/degraded states

### Phase B — first civic journey

- capability selection
- case model
- authority resolution
- document generation
- evidence capture
- review/approval
- submission state
- tracking

### Phase C — accountability and government intelligence

- office/service ratings
- officer/service experience
- positive recognition
- escalation graph
- bill/act/ordinance tracker
- constitutional/legal source comparison
- schemes/events intelligence
- government claim verification

### Phase D — document intelligence

- recipient registry
- postal/email verification
- CC resolution
- address correction workflow
- PDF/DOCX export
- correction history

### Phase E — resilient and decentralized capability

- Nostr adapter
- Nym adapter
- Reticulum adapter
- Freenet research adapter
- blockchain provenance adapter
- ZKP verification adapter

### Phase F — financial contribution

- contribution policy
- recipient registry
- payment adapter
- receipts/reconciliation
- transparency ledger/reporting
- audit controls
- compliance review

### Phase G — intelligence fabric

- OCR/CV/SAM
- VLM
- SLM/local AI
- RAG
- LLM/MoE/MLM
- LAM
- controlled agentic workflows
- evaluation/fallbacks

## 16. Verification gate

A feature is not considered complete merely because code exists or a screen renders.

```text
DESIGNED
  ↓
CONTRACTED
  ↓
IMPLEMENTED
  ↓
FUNCTIONAL
  ↓
TESTED
  ↓
FAILURE-TESTED
  ↓
SECURITY-VERIFIED
  ↓
PRIVACY-VERIFIED
  ↓
SOURCE/PROVENANCE-VERIFIED
  ↓
PRODUCTION-READY
```

Every milestone must record evidence in GitHub.

## 17. Decision log — locked principles

1. Full ecosystem, not MVP.
2. App + DApp are first product-building focus.
3. Dynamic Web/WebApp remains first-class and independent.
4. Android and iOS are independent runtimes.
5. DApp/Web3 is optional for users and ordinary civic flows.
6. Privacy and safety are by design and by default.
7. Nostr, Nym, Reticulum, Blockchain/ZKP and Freenet are capability/transport/verification tools, not universal dependencies.
8. AI is optional, replaceable and purpose-bound.
9. Good public service should be recognized as well as poor service corrected.
10. Allegations, ratings, verified findings and official determinations must remain distinct.
11. Citizen action includes complaints, grievances, RTI, petitions, representations, policy opinions, objections, appeals and escalation as appropriate.
12. Government information must be source-backed and freshness-aware.
13. Document recipient information must be verifiable and correctable with history.
14. Financial contribution must be transparent, auditable and must not purchase public influence.
15. No capability should become a single point of failure for unrelated capabilities.

**This file is a control document. Update it when a locked architecture decision changes; do not silently create conflicting plans elsewhere.**
