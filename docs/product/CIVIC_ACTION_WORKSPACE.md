# JANAVANI — Civic Action Workspace

**Status:** Canonical product definition proposal
**Date:** 27 August 2026
**Strategic parent:** `docs/strategy/DIGITAL_SWARAJ_ECOSYSTEM_STRATEGY.md`

## 1. Product definition

The Janavani Civic Action Workspace is the first complete product surface of the Janavani Civic Action Operating System.

It is a case-centric workspace that helps a citizen move from a real-world civic/public-service problem to structured facts, evidence, the appropriate authority, a reviewable civic action/document, submission, truthful delivery state, tracking, follow-up and outcome.

The Web/WebApp is the first product-building surface. The underlying case and capability contracts must remain independent of Web and reusable by Telegram, Mini App, Android, iOS, WhatsApp, Messenger, DApp and future interfaces.

## 2. Product promise

> Turn a real civic problem into a clear, evidence-backed, reviewable and trackable civic action with the least unnecessary citizen effort.

Janavani does not promise that a government authority will resolve an issue. It promises to help the citizen understand, prepare, communicate, track and follow up truthfully.

## 3. Core lifecycle

```text
Problem
  ↓
Case
  ↓
Understand
  ↓
Structure facts
  ↓
Collect evidence
  ↓
Identify authority
  ↓
Choose action
  ↓
Draft / compose
  ↓
Citizen review
  ↓
Citizen approval
  ↓
Submission
  ↓
Delivery / acknowledgement
  ↓
Tracking
  ↓
Follow-up
  ↓
Escalation where appropriate
  ↓
Outcome
```

## 4. Case as the atomic product object

A Case is the durable unit of citizen work.

Minimum conceptual fields:

- case identity;
- citizen-controlled identity/consent state;
- issue and intent;
- structured facts;
- jurisdiction/location where relevant;
- authority candidates and provenance;
- evidence references and verification state;
- documents/actions;
- review and approval state;
- submission attempts;
- truthful delivery state;
- acknowledgement/tracking references;
- follow-up state;
- escalation history;
- outcome;
- correction history;
- audit/provenance events.

A client must not create a parallel channel-specific case model unless an explicit adapter contract requires transient transport state.

## 5. First product workflows

Prioritize a narrow, high-friction wedge:

1. civic/public-service complaint;
2. grievance preparation and follow-up;
3. RTI preparation;
4. representation/petition;
5. evidence-backed municipal/service issue.

All workflows should use the same case lifecycle and shared capability contracts.

## 6. First Web release

### Create case

- free-form problem description;
- optional structured fields;
- location when relevant;
- privacy/consent choices;
- clear statement of what Janavani will do.

### Understand

- summarize the citizen's issue;
- identify missing facts;
- ask only necessary follow-up questions;
- preserve citizen corrections;
- distinguish generated interpretation from citizen-provided facts.

### Authority intelligence

- identify candidate authority;
- show rationale;
- expose source/provenance;
- show verified contact/address data where available;
- allow citizen correction/selection;
- never invent official recipients.

### Evidence

- upload documents/photos where supported;
- preserve metadata subject to privacy policy;
- distinguish user-provided evidence from extracted/generated interpretation;
- support verification/correction state.

### Action/document

- select complaint, grievance, RTI, representation, petition or other supported action;
- compose structured document;
- optionally use AI assistance;
- preserve deterministic path;
- show recipient fields and sources;
- allow citizen editing.

### Review and approval

Before consequential action, show:

- document content;
- recipients;
- attachments/evidence;
- material source claims;
- submission method;
- privacy/data-sharing implications;
- known uncertainty;
- final approval control.

### Submission

Record the actual state, for example:

```text
NOT_SUBMITTED
READY
SUBMISSION_ATTEMPTED
DELIVERED
ACKNOWLEDGED
FAILED
UNKNOWN
```

Never represent an attempted or queued action as successfully delivered without evidence.

### Tracking/follow-up

- maintain case timeline;
- store references and acknowledgements;
- schedule follow-up;
- prepare next action;
- support escalation only when applicable and evidence-supported.

## 7. AI policy

AI is optional assistance, not the product identity and not a mandatory dependency.

AI may support:

- issue understanding;
- extraction;
- translation;
- drafting;
- summarization;
- evidence assistance;
- authority research;
- quality review.

AI must not silently:

- invent official addresses;
- convert uncertain information into facts;
- submit consequential communication without required approval;
- expose unnecessary citizen data to a provider;
- become the only path through a critical workflow.

Provider/model implementations must remain replaceable.

## 8. Deterministic and degraded paths

Examples:

- AI unavailable → manual/deterministic document workflow remains available.
- OCR unavailable → manual evidence metadata entry remains available.
- Government search unavailable → saved/previously verified information remains visible with freshness status; no fabricated replacement.
- Submission provider unavailable → preserve the draft and report the actual state.
- Messaging channel unavailable → another authorized channel may be offered without changing the underlying case.

## 9. Privacy and safety defaults

The workspace follows privacy-by-design and safety-by-design:

- data minimization;
- purpose limitation;
- least privilege;
- explicit consent where required;
- independent client boundaries;
- user-controlled sharing;
- retention controls;
- provenance;
- auditable consequential actions;
- safe failure;
- explicit delivery state;
- human approval for high-impact external actions.

Choosing not to use an optional capability does not remove these protections.

## 10. Interface independence

The Web implementation is the first product surface, not the owner of the product.

Target relationship:

```text
Web ───────────────┐
Telegram ──────────┤
Mini App ──────────┤
Android ───────────┤
iOS ────────────────┤
WhatsApp ──────────┤
Messenger ─────────┤
DApp ──────────────┤
Future clients ────┘
          ↓
Capability contracts
          ↓
Case / workflow / domain services
```

No client should require another client to be running.

## 11. Success criteria for the first complete slice

The first slice is complete only when a test user can:

1. create a case;
2. describe the problem;
3. answer necessary clarification questions;
4. identify/select an authority with source information;
5. attach evidence;
6. produce a document/action;
7. review and edit it;
8. approve it;
9. submit through a supported mechanism;
10. receive a truthful delivery state;
11. see the case timeline;
12. prepare a follow-up.

The implementation must have automated tests for normal paths, authorization failures, malformed input, dependency failure and degraded operation.

## 12. Product metrics

Primary:

> Verified civic outcomes per 1,000 citizen-hours of effort.

Supporting:

- time to usable action;
- case completion rate;
- abandonment by stage;
- document edit/correction rate;
- submission success rate;
- acknowledgement capture rate;
- follow-up completion;
- outcome/resolution rate where measurable;
- factual correction rate;
- AI error rate;
- privacy/security incidents;
- percentage of critical workflows surviving optional dependency failure.

## 13. Explicit non-goals for the first release

Do not make the first release dependent on:

- blockchain;
- token economy;
- DAO governance;
- nationwide mesh;
- custom foundation model;
- custom hardware;
- complex decentralized identity;
- generalized social network.

These remain ecosystem capabilities/strategic directions where justified by later evidence.

## 14. Relationship to Digital Swaraj

The Civic Action Workspace is the product wedge through which the Digital Swaraj strategy becomes operational. The strategic doctrine remains above this product definition; the product does not replace or narrow the wider ecosystem.

Reference: `docs/strategy/DIGITAL_SWARAJ_ECOSYSTEM_STRATEGY.md`.
