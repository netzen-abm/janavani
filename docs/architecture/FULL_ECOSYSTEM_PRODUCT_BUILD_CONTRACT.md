# Janavani Full Ecosystem Product Build Contract

**Status:** ACTIVE — CANONICAL PRODUCT DIRECTION

## 1. Product definition

Janavani is a **full civic-governance ecosystem**, not an MVP project.

The WebApp and Telegram Bot are active product surfaces being developed in parallel. Neither is the product core. The platform core is the shared capability/domain infrastructure consumed by independent access surfaces.

## 2. Product law

> **Build the capability once. Govern it once. Reuse it everywhere.**

```text
Canonical Domain + Capability Infrastructure
                 │
       ┌─────────┼─────────┐
       │         │         │
    WebApp    Telegram   Mobile
       │         │         │
       └─────────┼─────────┘
                 │
       Future Mini App / WhatsApp /
       Messenger / DApp / Partners
```

A surface owns presentation, channel constraints, local UX and adapter concerns. It does not own canonical civic business logic.

## 3. Full product lifecycle

The canonical civic-action lifecycle is:

```text
Lived problem
  ↓
Case creation
  ↓
Fact / claim structuring
  ↓
Authority + jurisdiction intelligence
  ↓
Evidence capture / reference
  ↓
Document composition
  ↓
Citizen review + correction
  ↓
Consent + explicit consequential-action approval
  ↓
Submission preparation
  ↓
Verified submission
  ↓
Acknowledgement
  ↓
Tracking
  ↓
Follow-up
  ↓
Appeal / escalation / RTI where appropriate
  ↓
Outcome
  ↓
Accountability + public learning
```

A vertical slice is a **verification path through this lifecycle**, not a product scope boundary.

## 4. Development model

WebApp and Telegram may advance simultaneously when they share the same capability contract:

```text
                Shared Capability Contract
                    /             \
                   /               \
             WebApp adapter    Telegram adapter
                  |                  |
              UX state          conversation state
                  \                  /
                   \                /
                    canonical domain
```

Parallel development must not create:

- two Case models;
- two ownership models;
- two document engines;
- two evidence models;
- two submission state machines;
- two authority registries;
- two AI policy engines;
- two persistence authorities.

## 5. Convergence law

When duplicate generations are discovered:

1. identify the canonical capability;
2. classify every implementation as active, adapter, experimental, historical or obsolete;
3. preserve evidence/history before removal;
4. extract reusable behavior into the canonical capability;
5. migrate consumers one surface at a time;
6. verify tests and runtime behavior;
7. archive the superseded implementation;
8. delete only after an explicit archive/disposal gate.

No blind rewrite and no blind deletion.

## 6. Identity and authorization

Interface authentication and citizen identity are separate concerns.

The canonical request path is:

```text
Surface
  ↓
Interface authentication
  ↓
Trusted identity provider / adapter
  ↓
Principal + IdentityContext
  ↓
Authorization kernel
  ↓
Capability
  ↓
Repository / external adapter
```

A browser field, URL parameter, Telegram numeric ID, `actor_id`, or `X-Actor-ID` header is not a trusted citizen identity.

The current Web/API signed-assertion boundary is a transitional trusted-gateway contract. It is not a replacement for a production OIDC/passkey/cryptographic identity provider. Production deployment must use a properly managed identity gateway, short-lived assertions, issuer/audience validation, replay protection and secret/key rotation.

## 7. Consequential actions

Submission, external messaging, publication, deletion and other consequential operations require explicit authorization/approval.

The system must never infer approval merely from:

- model output;
- case readiness;
- possession of a service token;
- a client-supplied boolean;
- a prior unrelated consent.

The current `/submit` path deliberately stops at the authorization gate until the canonical approval capability is implemented.

## 8. AI contract

AI is a shared optional capability, not the product identity and not a mandatory pipeline.

AI may:

- understand;
- classify;
- extract;
- translate;
- draft;
- retrieve;
- suggest;
- assist with structured reasoning.

AI may not autonomously convert its own output into verified fact, citizen consent, identity, authorization or completed external action.

Every AI capability must define its source/provenance, uncertainty, data boundary, tool permissions and human/explicit-approval gate where consequential.

## 9. Evidence contract

Evidence is a first-class capability, not an attachment feature.

The ecosystem must preserve:

- original integrity;
- capture time distinct from submission time;
- source/channel;
- location semantics;
- transformation history;
- provenance;
- privacy class;
- transmission state;
- deletion/retention state.

Originals must never be silently overwritten by OCR, compression, redaction or model-derived artifacts.

## 10. Product quality gates

A capability progresses through:

```text
VISION
 → CONTRACTED
 → IMPLEMENTED
 → FUNCTIONAL
 → TESTED
 → SECURITY-VERIFIED
 → PRIVACY-VERIFIED
 → RUNTIME-VERIFIED
 → PRODUCTION-READY
 → OPERATED / MONITORED
```

No capability is considered complete because one interface demonstrates it.

## 11. Current execution priority

The ecosystem scope remains broad. Execution priority is determined by dependency criticality, user value, security and reuse:

### P0 — Shared product foundation
- Identity → authorization → resource ownership
- Canonical Case capability
- Capability/API contracts
- Repository and transaction boundaries
- Shared session/workflow model
- Evidence/document contracts

### P1 — Parallel product surfaces
- WebApp canonical capability client
- Telegram canonical capability adapter
- Shared authority intelligence
- Shared document composition
- Shared evidence/provenance path

### P2 — Complete civic-action lifecycle
- Explicit approval capability
- Submission adapters
- Acknowledgement/tracking
- Follow-up/escalation
- Notifications and delivery truth

### P3 — Ecosystem expansion
- Telegram Mini App
- WhatsApp / Messenger
- Android / iOS
- institutional/partner API
- expert/volunteer ecosystem
- accountability and public learning

### P4 — Advanced optional infrastructure
- local AI / SLM
- CV/VLM/SAM
- decentralized identity and verifiable credentials
- Nostr/IPFS/Nym/Reticulum and resilient transport
- mesh/satellite capabilities
- other future technologies justified by concrete capability needs

## 12. Definition of success

Janavani is successful when a citizen can move through the civic-action lifecycle using whichever access surface is appropriate, while the underlying capabilities remain consistent, privacy-preserving, evidence-aware, auditable, resilient and independent of any one provider, interface or model.

**The ecosystem is the product.**
