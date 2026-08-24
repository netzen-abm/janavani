# JanaVani Ecosystem Charter

**Status:** Canonical direction document  
**Date:** 24 August 2026  
**Scope:** Full JanaVani ecosystem, with App/DApp and dynamic WebApp as the immediate build focus

## 1. Purpose

JanaVani is being built as a full citizen-governance ecosystem for India, not as a single application, chatbot, website, blockchain product, or AI product.

The ecosystem should help people understand public institutions and government action, collect and evaluate evidence, make lawful civic representations, communicate with the appropriate authority, track responses, escalate when appropriate, recognize good public service, identify unresolved problems, and support public learning and accountability.

The constitutional and civic framing of the project is grounded in the Constitution of India and applicable law. JanaVani must present legal and constitutional analysis carefully, distinguish evidence from inference, and avoid claiming legal authority that it does not possess.

## 2. North Star

```text
Citizen reality
    -> evidence and understanding
    -> correct authority / institution
    -> informed civic action
    -> submission / communication
    -> acknowledgement and tracking
    -> follow-up / escalation where appropriate
    -> response / outcome
    -> accountability and public learning
```

The ecosystem should make this lifecycle available through multiple independent access surfaces and technologies.

## 3. Non-Negotiable Architectural Principle

> **Every feature and capability exists independently. The user chooses whether to participate in or enable it. Failure or unavailability of one optional capability must not unnecessarily prevent unrelated capabilities from operating.**

This means:

- capability presence is a platform requirement;
- capability participation is user-controlled;
- optional technology is never a hidden runtime dependency;
- one transport, provider, model, client, database, or integration must not become a single point of failure for the ecosystem;
- degraded operation is preferable to unnecessary total failure;
- every capability must expose explicit health and availability state;
- interfaces consume capability contracts rather than owning business logic;
- adapters isolate external technologies from the core domain.

### Capability presence vs participation

Freenet is a mandatory ecosystem capability, but Freenet participation is explicitly opt-in. The same principle applies to Nostr, Nym, Reticulum, blockchain/Web3, ZKP, AI providers, analytics, messaging integrations, and other optional technologies.

A user who does not enable a capability must still be able to use unrelated JanaVani functionality.

## 4. Client Surfaces

The ecosystem is intended to support independent clients/access surfaces including:

- Android application
- iOS application
- Dynamic interactive WebApp / website
- DApp / Web3 interface
- Telegram application/bot
- Telegram Mini App
- WhatsApp integration
- Messenger integration
- APIs and institutional integrations
- future interfaces not yet known

No client is the canonical owner of civic business logic. Shared contracts and capabilities are the source of reusable behavior.

## 5. Network and Data Capability Fabric

JanaVani may support multiple independent network, transport, identity, storage, and verification technologies, including:

- Nostr
- Nym Mixnet
- Reticulum Mesh
- Freenet
- blockchain networks
- zero-knowledge proofs
- conventional Internet services
- local/offline storage and synchronization
- future decentralized or privacy-enhancing protocols

These are integration capabilities, not assumptions about the product's identity. Each integration requires an explicit capability-level justification, security model, consent model, failure policy, and test coverage.

## 6. AI and Intelligence Fabric

AI is replaceable infrastructure and a set of independently selectable capabilities, not the sole source of truth and not the identity of JanaVani.

The ecosystem may support independent or composable capabilities including:

- OCR
- Computer Vision
- SAM / segmentation
- VLM
- SLM
- LLM
- MLM
- MoE
- LAM
- RAG
- Agentic AI
- translation and speech systems
- local models
- remote/provider models

A failure in one model/provider must not unnecessarily disable ordinary civic functions. Critical workflows must have deterministic or degraded paths where practical.

AI output must be distinguishable from source evidence. Important claims should carry provenance and, where feasible, allow the user to inspect the supporting source material.

## 7. Civic Capability Landscape

The ecosystem scope includes, but is not limited to:

### Government and civic information

- central and state government schemes
- public services
- departments and offices
- officers and institutional roles
- elected representatives including MPs, MLAs and local representatives
- government events and public programmes
- laws, rules, notifications, bills, ordinances and policy changes
- government claims and performance information

### Accountability and service experience

- government service ratings and reviews
- office and service experience reporting
- officer/service recognition
- evidence-based reporting of unresolved or poor service
- department-head escalation
- administrative-head escalation
- appropriate elected-representative escalation
- response and resolution tracking
- correction, appeal and dispute mechanisms

Citizen reports, allegations, verified findings, official responses, and system-generated analysis must remain visibly distinct.

### Legislative and constitutional intelligence

JanaVani should be able to track relevant bills, Acts, ordinances, rules, notifications and policy changes; explain their practical significance; summarize source material; and, where requested, evaluate proposals against applicable constitutional principles and the project's defined constitutional analysis framework.

The system may identify potential concerns or tensions, but must avoid presenting an AI assessment as a judicial determination.

Users should be able to express opinions or objections and generate relevant lawful representations.

### Civic document generation

The ecosystem should support context-appropriate generation of:

- complaints
- grievances
- petitions
- representations
- RTI applications
- appeals
- objections
- follow-up letters
- escalation letters
- citizen opinions on policies
- other lawful civic communications

Documents should support PDF and DOCX output where applicable, with authority/address information populated from verified records. Postal and email delivery details should be separately verified, versioned, and correctable. User-submitted corrections must enter a controlled verification workflow rather than silently changing authoritative records.

### Financial contribution and support

The ecosystem should support transparent contribution workflows where legally and operationally appropriate, including support for good public-service outcomes and accountable civic initiatives.

Financial contribution must be an isolated subsystem with explicit accounting/provenance boundaries:

```text
source -> authorization -> transaction -> allocation
      -> expenditure -> evidence -> audit trail -> public reporting
```

Blockchain may provide optional verification or publication mechanisms; it must not be a mandatory dependency for ordinary contribution functionality.

## 8. Privacy, Safety and User Control

Privacy by Design and Privacy by Default are architectural requirements.

Safety by Design and Safety by Default are architectural requirements.

The ecosystem should favor:

- data minimization
- explicit consent
- user-controlled capability activation
- least privilege
- local processing where practical
- optional anonymous workflows where lawful and appropriate
- clear retention controls
- secure evidence handling
- auditable high-impact actions
- clear delivery state
- reversible configuration changes where feasible

Users should be able to understand what a capability does, what data it needs, what external systems it contacts, and what happens if they disable it.

## 9. Evidence, Provenance and Correction

JanaVani must separate three layers:

1. **Evidence** — source documents, official records, citizen submissions, media, measurements and other identified material.
2. **Analysis** — extraction, comparison, summarization, model output and human review.
3. **Action** — complaint, RTI, objection, petition, escalation, publication or other user-authorized action.

An inference must never silently become a fact.

Important data should carry provenance, verification state, source date, correction history where relevant, and responsible source type.

## 10. Human Approval and Agentic Boundaries

Agentic AI may assist with research, extraction, drafting, routing, comparison, monitoring and other permitted operations.

High-impact actions require explicit permission and appropriate user confirmation. This includes, depending on the workflow:

- submitting an official communication;
- publishing a serious allegation;
- changing authoritative profile information;
- executing financial transactions;
- making external commitments on behalf of a user.

Tool permissions must be scoped and auditable.

## 11. Future Technology Independence

JanaVani must not hard-code an evolutionary chain such as Web2 -> Web3 -> Web4 -> Web5 -> Web6.

Future technologies should enter as adapters or capabilities behind stable contracts. The architecture must make it practical to add a new protocol, network, identity mechanism, storage system, interaction model, AI provider, or future Web paradigm without redesigning unrelated parts of the ecosystem.

The desired evolution model is:

```text
stable JanaVani core
        |
   capability contract
        |
   new implementation / adapter
        |
   registration + policy + consent
        |
   independent verification
```

## 12. Failure Isolation Requirement

Every significant capability must define:

- availability states;
- timeout and retry behavior;
- fallback/degraded behavior;
- dependency boundaries;
- data ownership/storage boundary;
- failure reporting;
- recovery behavior;
- tests demonstrating non-cascading failure.

Examples of required independence:

- Freenet failure must not disable the normal app.
- Blockchain failure must not disable ordinary civic workflows.
- AI-provider failure must not disable document generation or access to stored evidence.
- Nostr failure must not disable WebApp functionality.
- Telegram failure must not disable Android/iOS/WebApp.
- A government API failure must not erase locally retained user state or unrelated government information.

## 13. App / DApp First Implementation Focus

The immediate product-building focus is:

1. Android application foundation
2. iOS application foundation
3. DApp/Web3 foundation
4. Dynamic interactive WebApp foundation
5. Shared capability contracts and registry
6. Consent/privacy/security control plane
7. Local-first state and offline/degraded operation
8. First complete civic vertical slice

The first vertical slice should prove the architecture with a real workflow rather than a static UI:

```text
issue
 -> understanding
 -> authority discovery
 -> evidence
 -> lawful action/draft
 -> user review
 -> document generation
 -> submission/delivery
 -> acknowledgement/tracking
 -> follow-up/escalation
```

This is the first implementation slice, not a reduction of ecosystem scope.

## 14. Architectural Test Gates

A capability is not complete merely because its happy path works.

The verification ladder is:

```text
VISION
 -> DESIGNED
 -> IMPLEMENTED
 -> FUNCTIONAL
 -> TESTED
 -> SECURITY-VERIFIED
 -> PRIVACY-VERIFIED
 -> FAILURE-ISOLATED
 -> PRODUCTION-READY
```

Architecture tests should prove optional capabilities can be disabled or fail without cascading into unrelated capabilities.

## 15. Repository Direction Control

This document is the durable direction anchor for decisions discussed across planning sessions.

When a new proposal conflicts with this charter, the implementation should either:

1. preserve the charter;
2. explicitly document an exception; or
3. amend the charter through an Architecture Decision Record.

Do not allow major architectural decisions to live only in chat history.

## 16. What This Charter Does Not Mean

Independence does not mean duplicating every capability in every client or banning all useful composition.

A workflow may legitimately compose capabilities when the user requests it. For example, OCR may feed RAG, RAG may assist an LLM, and an agent may use a document service. The requirement is that the failure or disabling of one optional capability does not unnecessarily destroy unrelated capabilities, and that the composition is explicit, bounded, observable, and replaceable.

## 17. Long-Term Outcome

The target is a resilient, privacy-preserving, user-controlled citizen-governance ecosystem in which technology serves civic capability rather than defining or constraining it.

**The ecosystem is the product. The clients, networks, AI systems, protocols, and future technologies are independently selectable means of accessing or extending it.**
