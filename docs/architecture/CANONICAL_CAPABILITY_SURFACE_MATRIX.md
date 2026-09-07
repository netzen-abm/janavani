# Janavani — Canonical Capability × Surface Matrix

**Status:** ACTIVE ECOSYSTEM CONVERGENCE CONTROL DOCUMENT  
**Baseline:** `main`  
**Purpose:** Track how canonical capabilities are consumed by all Janavani product surfaces without allowing channel-specific business logic to become a second implementation.

## Governing rule

> **One capability, one canonical owner, many access surfaces.**
>
> Capability availability is an ecosystem responsibility. Capability selection and AI invocation are user-controlled.

A surface may expose a capability differently because of platform constraints, but it must not create a parallel domain implementation.

This is a **full-product ecosystem control document**, not an MVP completion checklist. A vertical slice is a verification sequence inside the larger product, not the product boundary.

## Status vocabulary

- **CANONICAL:** authoritative implementation/contract identified.
- **ADAPTER:** surface integration should remain thin and channel-specific.
- **PARTIAL:** useful implementation exists but the complete lifecycle is not verified.
- **MISSING:** capability is registered/designed but no verified active implementation is mapped.
- **BLOCKED:** implementation depends on an unresolved security, identity, persistence, provider, or platform contract.
- **PARKED:** intentionally deferred because its prerequisite/value/risk case is not yet satisfied; it remains part of the ecosystem architecture unless explicitly retired.

## Product surfaces

| Surface | Current role | Current state | Rule |
|---|---|---|---|
| Public Website | Public information/discoverability surface | ACTIVE | Never become the platform business-logic owner |
| WebApp / Dioxus | Primary interactive product surface | PARTIAL | Consume shared capabilities; no business logic duplication |
| Telegram Bot | Messaging access surface | PARTIAL | Adapter only; consume the same Case/Authority/Document capabilities |
| Telegram Mini App | Rich Telegram UI | MISSING | Consume the same shared capability contracts |
| Android | Native product surface | ARCHITECTURE | Consume shared contracts; own only native UX/integration |
| iOS | Native product surface | ARCHITECTURE | Consume shared contracts; own only native UX/integration |
| WhatsApp | Messaging access surface | ARCHITECTURE | Adapter only |
| Messenger | Messaging access surface | ARCHITECTURE | Adapter only |
| DApp / decentralized interfaces | Optional product/access surface | ARCHITECTURE | Capability-driven, never a mandatory dependency |
| API / institutional integrations | Integration surface | IN PROGRESS | Expose canonical capabilities, policy and provenance |
| Future partner/third-party clients | Ecosystem extension surface | ARCHITECTURE | Contract-governed access only |

## First complete vertical slice

The immediate verification sequence is:

```text
Citizen problem
    ↓
Case
    ↓
Structure facts / claims
    ↓
Authority discovery
    ↓
Evidence reference
    ↓
Document draft
    ↓
Citizen review + correction
    ↓
Explicit approval / consent
    ↓
Submission preparation
    ↓
Acknowledgement / truthful tracking
```

This is **not an MVP boundary**. It is the first end-to-end capability chain used to prove that the shared platform can support the broader ecosystem. External submission remains gated until identity, authorization, consent, destination verification, and submission adapters are production-ready.

## Capability matrix

| Canonical capability | Canonical owner currently mapped | WebApp | Telegram Bot | Mini App | Current blocker / next action |
|---|---|---|---|---|---|
| `JNV-CIVIC-COMPLAINT` | `src/core/civic_case.py` + civic-action composition | PARTIAL | PARTIAL | MISSING | Connect both surfaces to the canonical Case capability and verify lifecycle |
| `JNV-CIVIC-GRIEVANCE` | Case capability (design) | MISSING | MISSING | MISSING | Reuse Case; add purpose-specific workflow |
| `JNV-CIVIC-RTI` | Case + Document (design) | MISSING | MISSING | MISSING | Add reusable RTI workflow |
| `JNV-CIVIC-PETITION` | Case + Document (design) | MISSING | MISSING | MISSING | Add reusable petition workflow |
| `JNV-CIVIC-OBJECTION` | Case + Document (design) | MISSING | MISSING | MISSING | Add reusable objection workflow |
| `JNV-CIVIC-APPEAL` | Case + Document (design) | MISSING | MISSING | MISSING | Add response/tracking lifecycle first |
| `JNV-GOV-OFFICE-SEARCH` | `src/services/authority_service.py` + AuthorityRepository | PARTIAL | ADAPTER | MISSING | Replace text-only rendering with structured capability response |
| `JNV-GOV-OFFICER-SEARCH` | Authority design | MISSING | MISSING | MISSING | Define lawful/public-data contract |
| `JNV-GOV-SCHEME-SEARCH` | Design | MISSING | MISSING | MISSING | Define authoritative source registry |
| `JNV-GOV-SCHEME-ELIGIBILITY` | Design | MISSING | MISSING | MISSING | Define non-official assessment boundary |
| `JNV-ACCOUNTABILITY-OFFICE-REVIEW` | Feedback router / design | MISSING | PARTIAL | MISSING | Replace channel/file storage with canonical feedback capability |
| `JNV-ACCOUNTABILITY-OFFICER-REVIEW` | Design | MISSING | MISSING | MISSING | Define safeguards and evidence distinction |
| `JNV-ACCOUNTABILITY-REPRESENTATIVE-REVIEW` | Design | MISSING | MISSING | MISSING | Define sourced-data model |
| `JNV-ACCOUNTABILITY-GOV-PERFORMANCE` | Design | MISSING | MISSING | MISSING | Define public dataset/provenance model |
| `JNV-ACCOUNTABILITY-TRANSFER-CONCERN` | Design | MISSING | MISSING | MISSING | Define evidence and routing contract |
| `JNV-ACCOUNTABILITY-MISBEHAVIOUR` | Design | MISSING | MISSING | MISSING | Define high-risk allegation handling |
| `JNV-ACCOUNTABILITY-CORRUPTION` | Design | MISSING | MISSING | MISSING | High-risk security/whistleblower boundary first |
| `JNV-DOC-GENERATE` | `src/documents/*` + civic-action composition | PARTIAL | PARTIAL | MISSING | Converge existing PDF/DOCX generators behind one provider contract |
| `JNV-DOC-ADDRESS-CORRECTION` | Design | MISSING | MISSING | MISSING | Build verification/provenance workflow |
| `JNV-DOC-EXPORT` | Existing artifact providers | PARTIAL | PARTIAL | MISSING | Verify browser-safe export and artifact lifecycle |
| `JNV-EVIDENCE-CAPTURE` | Evidence contract | MISSING | MISSING | MISSING | Local-first capture boundary before upload |
| `JNV-EVIDENCE-PROVENANCE` | Evidence contract | PARTIAL | PARTIAL | MISSING | Implement source/time/transformation metadata |
| `JNV-EVIDENCE-BLOCKCHAIN-ANCHOR` | Design | PARKED | PARKED | PARKED | Optional provider; activate only with capability-level justification |
| `JNV-EVIDENCE-ARCHIVE` | Architecture | PARTIAL | PARTIAL | MISSING | Formalize retention/archive operations |
| `JNV-WB-SUBMIT` | Design | BLOCKED | BLOCKED | BLOCKED | Identity, authorization, consent, destination and submission adapter gates |
| `JNV-WB-CASE` | Design | BLOCKED | BLOCKED | BLOCKED | Real identity/ownership boundary before broad surface exposure |
| `JNV-EXPERT-REGISTER` | Design | ARCHITECTURE | ARCHITECTURE | ARCHITECTURE | Later ecosystem expansion with verification safeguards |
| `JNV-EXPERT-REVIEW` | Design | ARCHITECTURE | ARCHITECTURE | ARCHITECTURE | Review/provenance/conflict controls first |
| `JNV-AI-OCR` | Design | MISSING | MISSING | MISSING | Add governed AI capability after deterministic path |
| `JNV-AI-VISION` | Design | MISSING | MISSING | MISSING | Add only for concrete product need |
| `JNV-AI-RAG` | Design | MISSING | MISSING | MISSING | Build source/version/citation contract first |
| `JNV-AI-SLM` | Design | PARKED | PARKED | PARKED | Concrete on-device use case required |
| `JNV-AI-LLM` | AI capability boundary | PARTIAL | PARTIAL | MISSING | Keep provider behind governed shared capability |
| `JNV-AI-AGENT` | Agent capability design | MISSING | MISSING | MISSING | Implement scoped tools + approval gates before activation |
| `JNV-SOS-PERSONAL` | Dioxus SOS interface / architecture | PARTIAL | MISSING | MISSING | Native transport and truthful delivery contract |
| `JNV-SOS-SILENT` | Architecture | MISSING | MISSING | MISSING | Native platform work later |
| `JNV-SOS-MESH` | Architecture | PARKED | PARKED | PARKED | Transport adapter milestone |
| `JNV-SOS-SATELLITE` | Architecture | PARKED | PARKED | PARKED | Provider/regulatory verification |
| `JNV-SOS-ROUTER` | Architecture | PARKED | PARKED | PARKED | Transport health/policy implementation |
| `JNV-SOS-DELIVERY` | Architecture | PARKED | PARKED | PARKED | Truthful delivery state implementation |

## Surface contracts

### WebApp

The current Dioxus application is a **product surface under convergence**, not a disposable MVP shell. It currently sends free-form text to a legacy `/agent/draft` path and contains a hard-coded example location plus a simulated decentralized result. That behavior must not become the canonical Case implementation.

Target:

```text
Dioxus UI
   ↓
Typed capability client
   ↓
Canonical Case / Authority / Evidence / Document capabilities
   ↓
Shared infrastructure
```

### Telegram Bot

The bot is an independent access surface and now uses the canonical CivicCase repository for `/check` and generated-case persistence. Remaining legacy areas include conversation preview/generation compatibility and legacy rating storage. These must converge into shared capabilities without making Telegram the owner of them.

Target:

```text
Telegram adapter
   ↓
Conversation / capability orchestration
   ↓
Canonical Case / Authority / Evidence / Document capabilities
   ↓
Shared infrastructure
```

### Telegram Mini App

No implementation is promoted to canonical status yet. It must consume the same API/capability contracts as WebApp and Telegram Bot and must not become another business-logic implementation.

## Parallel product development rule

WebApp and Telegram are explicitly developed **in parallel** when they consume the same canonical capability contract. Parallel development means parallel adapters and UX, not parallel domain implementations.

The same rule applies when Android, iOS, WhatsApp, Messenger, DApp or partner integrations become active.

## Security and privacy gates

Before a capability is marked `COMPLETE`:

1. Interface authentication is distinct from citizen identity.
2. User-supplied actor IDs are never treated as trusted HTTP identity.
3. Case ownership/access control is enforced by the identity → authorization → repository path.
4. Sensitive evidence remains local-first unless an explicitly authorized capability requires transmission.
5. AI output never becomes a verified fact merely because a model produced it.
6. Consequential external actions require explicit user confirmation.
7. Attempted transmission is never reported as delivery without acknowledgement.
8. Provider failure does not break unrelated capabilities.

## Completion rule

This matrix is a planning/control artifact. It does not promote implementation status by itself. A capability becomes `COMPLETE` only when implementation, tests, runtime verification, security/privacy review and documentation satisfy the master completion gate.
