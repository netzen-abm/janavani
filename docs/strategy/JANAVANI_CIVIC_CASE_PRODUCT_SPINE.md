# Janavani Product Spine: Civic Case Lifecycle

**Status:** Proposed canonical product rebaseline  
**Authority:** Product/architecture alignment document; subordinate to `docs/governance/CANONICAL_MAIN_RULESET.md` and repository source-of-truth documents  
**Decision:** Janavani's primary product abstraction is the **Civic Case**, not a government portal, credential broker, chatbot, or individual access surface.

## 1. Product thesis

Janavani is a citizen-controlled civic action infrastructure.

Its durable job is to help a citizen:

1. understand a civic situation;
2. structure it as a case;
3. collect and relate evidence;
4. identify the responsible authority and jurisdiction;
5. prepare an appropriate civic action;
6. obtain the required consent/review/approval;
7. submit or hand off through an appropriate channel;
8. record the authoritative response;
9. track the case;
10. determine and execute the next lawful action;
11. reach and record an outcome;
12. optionally contribute appropriately protected learning.

The government service, API, portal, messaging channel, AI model, database, storage provider, blockchain, or transport is an implementation mechanism around that lifecycle—not the product's primary identity.

## 2. Canonical product spine

```text
Citizen situation
      |
      v
Understand
      |
      v
Civic Case
      |
      +---- Context
      +---- Evidence + provenance
      +---- Authority + jurisdiction
      |
      v
Civic Action
      |
      v
Review / Consent / Authorization
      |
      v
Submission / Handoff
      |
      v
Authoritative response
      |
      v
Case timeline + status
      |
      v
Next action
      |
      v
Outcome
      |
      v
Optional protected civic learning
```

## 3. Core ownership boundary

### Janavani owns

- case structure and lifecycle;
- citizen-controlled context;
- evidence references and provenance structure;
- authority discovery and verified service knowledge;
- action composition and document preparation;
- privacy/data minimization decisions;
- consent and authorization orchestration;
- user review and consequential-action confirmation;
- submission/handoff orchestration;
- truthful status and recovery semantics;
- follow-up workflow;
- case timeline;
- outcome recording;
- optional aggregation/learning under explicit privacy boundaries.

### External systems own

- their authentication and authorization;
- their authoritative transaction processing;
- their official records;
- their adjudication/decision;
- their official acknowledgement and status;
- their service-specific credentials and security controls.

Janavani must not imply that it has completed or verified an external transaction unless the external system provides evidence supporting that state.

## 4. Access-surface rule

Web, Android, iOS, Telegram, Telegram Mini App, WhatsApp, Messenger, DApp and future surfaces are independent adapters/clients.

A surface failure must not invalidate the Civic Case or disable unrelated surfaces.

All surfaces consume shared capabilities through canonical contracts.

## 5. External-service rule

External government and civic services are delivery/integration targets, not the centre of the architecture.

Preferred order:

1. official API/SDK;
2. official OAuth/SSO/deep-link/handoff;
3. official artifact exchange;
4. human-guided browser handoff;
5. browser automation only where explicitly permitted and justified;
6. scraping only for lawful research/data-ingestion use, never as an assumed transaction mechanism.

Opening an external service does not authorize Janavani to transmit citizen data.

## 6. Credential rule

Janavani must not become a universal citizen government-password vault.

Where an external service supports a standard authorization flow, prefer the external service's authentication and OS/browser-managed secure credentials.

Janavani may retain the minimum connection/session metadata required for the citizen to understand and control a connection, but must not treat citizen credentials as ordinary Janavani application data.

## 7. AI rule

AI is a governed capability, not the product centre.

AI may assist with:

- issue understanding;
- classification;
- authority/service discovery;
- evidence organization;
- drafting;
- response interpretation;
- next-action explanation;
- pattern discovery.

AI must not silently:

- invent official destinations;
- claim submission success;
- invent acknowledgement numbers;
- represent an unverified inference as an authoritative fact;
- bypass authorization or consent;
- perform consequential external actions without the canonical approval path.

Critical workflows require deterministic or human-reviewable fallback where practical.

## 8. Case state model

The canonical lifecycle should support, at minimum:

```text
DISCOVERED
SERVICE_IDENTIFIED
SERVICE_VERIFIED
READY_FOR_ACTION
REVIEW_REQUIRED
APPROVED
SUBMITTED
EXTERNALLY_ACKNOWLEDGED
UNDER_PROCESSING
ACTION_REQUIRED
RESOLVED
PARTIALLY_RESOLVED
REJECTED
WITHDRAWN
ESCALATED
UNKNOWN
FAILED
EXPIRED
REVOKED
```

Implementations may use a more detailed internal state model, but externally visible states must remain truthful and must distinguish Janavani observations from external authoritative states.

## 9. Product primitives

The first-class product primitives are:

- Civic Case
- Case Context
- Evidence Reference
- Authority Record
- Civic Action
- Document Artifact
- Consent/Authorization Decision
- Submission/Handoff
- External Response
- Case Event
- Follow-up Action
- Outcome
- Optional Civic Learning Record

These primitives should map to the existing capability registry and canonical architecture rather than creating a competing taxonomy.

## 10. What is explicitly not a primary Janavani product

The following are not primary product identities:

- government portal aggregator;
- universal government login;
- universal credential manager;
- universal browser/RPA layer;
- AI chatbot;
- Telegram bot;
- complaint/PDF generator;
- blockchain/DApp;
- Nostr/Reticulum/Freenet transport;
- a single government API;
- a single database provider.

Each may be a capability, adapter, integration, or future technology where justified by the canonical contracts.

## 11. Product success criterion

A citizen should be able to answer:

> **What is my civic case, what do I know, what evidence supports it, who is responsible, what have I done, what did the authority actually say, what is the current state, and what can I do next?**

If Janavani can reliably answer those questions while preserving citizen control, provenance, privacy, and truthful state, the core product is working.

## 12. Relationship to existing architecture

This document consolidates the product interpretation already present across:

- `docs/JANAVANI_NORTH_STAR.md`
- `docs/JANAVANI_MASTER_ARCHITECTURE.md`
- `docs/JANAVANI_PRODUCT_LANDSCAPE.md`
- `docs/architecture/CANONICAL_CIVIC_ACTION_SPINE.md`
- `docs/architecture/SHARED_CAPABILITY_SPINE_PLAN.md`
- `docs/architecture/CIVIC_CASE_DATABASE_CONTRACT.md`
- `docs/architecture/CASE_LIFECYCLE_SEMANTICS.md`
- `docs/architecture/CONSEQUENTIAL_OPERATION_GATE.md`
- `docs/architecture/CAPABILITY_GATEWAY_CONTRACT.md`
- `docs/architecture/EXTERNAL_TOOL_REUSE_AND_DELEGATION_CONTRACT.md`

It does not replace the normative contracts above. Its purpose is to make their shared product centre explicit.

## 13. Decision record

The previously considered concept of a Janavani-managed universal government-service login/credential layer is **not adopted as a primary product direction**.

Reason:

- it makes external portals the centre of the product;
- it creates disproportionate credential/security risk;
- it duplicates capabilities already provided by external systems;
- it introduces fragile browser automation pressure;
- it does not exploit Janavani's strongest existing architecture: case, evidence, authority, action, provenance, consent, submission, response, follow-up and outcome;
- it conflicts with the ecosystem principle that external providers remain authoritative for their own transactions.

The reusable portion of that concept remains valid only as **external-service integration/handoff capability** under the external-tool reuse contract.

## 14. Implementation principle

Do not build a new monolithic "Civic Case OS" subsystem solely because this document names the product spine.

Instead:

```text
Existing canonical contracts
        |
        v
Converge around Civic Case
        |
        v
Remove duplicate generations only after evidence
        |
        v
Verify actual runtime behavior
        |
        v
Implement the highest-value missing capability
```

The immediate engineering objective is therefore **convergence and verification**, not architectural expansion.
