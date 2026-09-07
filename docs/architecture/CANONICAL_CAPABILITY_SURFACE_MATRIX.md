# Janavani — Canonical Capability × Surface Matrix

**Status:** ACTIVE CONVERGENCE CONTROL DOCUMENT  
**Baseline:** `main` at `79c21bfdf76bc4c8b4c16170391cf8e4f8f863b8`  
**Purpose:** Track which canonical capabilities are consumed by the first product surfaces without allowing channel-specific business logic to become a second implementation.

## Governing rule

> **One capability, one canonical owner, many access surfaces.**
>
> Capability availability is an ecosystem responsibility. Capability selection and AI invocation are user-controlled.

A surface may expose a capability differently because of platform constraints, but it must not create a parallel domain implementation.

## Status vocabulary

- **CANONICAL:** authoritative implementation/contract identified.
- **ADAPTER:** surface integration should remain thin and channel-specific.
- **PARTIAL:** useful implementation exists but the complete lifecycle is not verified.
- **MISSING:** capability is registered/designed but no verified active implementation is mapped.
- **BLOCKED:** implementation depends on an unresolved security, identity, persistence, provider, or platform contract.
- **PARKED:** intentionally deferred; not part of the current vertical slice.

## Current product surfaces

| Surface | Current role | Current state | Rule |
|---|---|---|---|
| WebApp / Dioxus | Primary product surface | PARTIAL | Consume shared capabilities; no business logic duplication |
| Telegram Bot | Messaging access surface | PARTIAL | Adapter only; consume the same Case/Authority/Document capabilities |
| Telegram Mini App | Rich Telegram UI | MISSING | Build after WebApp capability contracts are verified |
| Android | Future native surface | PARKED | Consume shared contracts |
| iOS | Future native surface | PARKED | Consume shared contracts |
| WhatsApp | Future messaging surface | PARKED | Consume shared contracts |
| Messenger | Future messaging surface | PARKED | Consume shared contracts |
| DApp | Future decentralized surface | PARKED | Consume shared contracts |

## First complete vertical slice

The immediate product target is:

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

For the first demonstrable slice, actual external submission remains out of scope until identity, authorization, consent, destination verification, and submission adapters are production-ready.

## Capability matrix

| Canonical capability | Canonical owner currently mapped | WebApp | Telegram Bot | Mini App | Current blocker / next action |
|---|---|---|---|---|---|
| `JNV-CIVIC-COMPLAINT` | `src/core/civic_case.py` + civic-action composition | PARTIAL | PARTIAL | MISSING | Connect UI workflow to Case capability and verify lifecycle |
| `JNV-CIVIC-GRIEVANCE` | Case capability (design) | MISSING | MISSING | MISSING | Reuse Case; add purpose-specific workflow |
| `JNV-CIVIC-RTI` | Case + Document (design) | MISSING | MISSING | MISSING | Add RTI workflow after complaint slice |
| `JNV-CIVIC-PETITION` | Case + Document (design) | MISSING | MISSING | MISSING | Add after first slice |
| `JNV-CIVIC-OBJECTION` | Case + Document (design) | MISSING | MISSING | MISSING | Add after first slice |
| `JNV-CIVIC-APPEAL` | Case + Document (design) | MISSING | MISSING | MISSING | Add after tracking/response lifecycle |
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
| `JNV-EVIDENCE-BLOCKCHAIN-ANCHOR` | Design | PARKED | PARKED | PARKED | Optional provider; not required for first slice |
| `JNV-EVIDENCE-ARCHIVE` | Architecture | PARTIAL | PARTIAL | MISSING | Formalize retention/archive operations |
| `JNV-WB-SUBMIT` | Design | PARKED | PARKED | PARKED | High-risk security milestone |
| `JNV-WB-CASE` | Design | PARKED | PARKED | PARKED | High-risk security milestone |
| `JNV-EXPERT-REGISTER` | Design | PARKED | PARKED | PARKED | Later ecosystem expansion |
| `JNV-EXPERT-REVIEW` | Design | PARKED | PARKED | PARKED | Later ecosystem expansion |
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

## Surface contract

### WebApp

The current Dioxus application is a **product shell**, not yet the complete civic-action workspace. It currently sends free-form text to a legacy `/agent/draft` path and contains a hard-coded example location plus a simulated decentralized result. That behavior must not become the canonical Case implementation.

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

The existing bot already has a useful adapter boundary and composes generation dependencies at startup. Its remaining legacy paths are:

- `/check` reads legacy `database/complaints.jsonl`.
- `/rate` writes legacy `database/ratings.jsonl`.
- conversation session state remains process-local.
- generation still contains a migration bridge into the Case model.

Immediate convergence work is to remove the Case tracking dependency on JSONL and make the Case repository authoritative.

### Telegram Mini App

No implementation is promoted to canonical status yet. It should consume the same API/capability contracts as WebApp and Telegram Bot and must not become another business-logic implementation.

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
