# JANAVANI — Case & Capability Contract

**Status:** Canonical convergence contract proposal
**Date:** 27 August 2026
**Parent strategy:** `docs/strategy/DIGITAL_SWARAJ_ECOSYSTEM_STRATEGY.md`
**Product:** `docs/product/CIVIC_ACTION_WORKSPACE.md`

## 1. Purpose

This document defines the boundary between Janavani access surfaces, shared capabilities, and the durable Case object.

The objective is to prevent channel-specific business logic and to make the same civic-action lifecycle usable through Web/WebApp, Telegram, Mini App, Android, iOS, WhatsApp, Messenger, DApp and future interfaces.

## 2. Core invariant

> A Case is the durable unit of citizen civic work. A capability is the reusable unit of system behavior. An access surface is an independent way to invoke those capabilities.

Therefore:

```text
Access Surface
    ↓
Capability Request
    ↓
Capability Contract
    ↓
Domain / Workflow / Service
    ↓
Repositories / Providers / Adapters
    ↓
Capability Result
    ↓
Access Surface
```

## 3. Case boundary

The Case owns civic-work state, not transport-specific presentation state.

Conceptual lifecycle:

```text
OPEN
 ↓
UNDERSTANDING
 ↓
EVIDENCE_COLLECTION
 ↓
AUTHORITY_SELECTION
 ↓
ACTION_PREPARATION
 ↓
REVIEW
 ↓
APPROVED
 ↓
SUBMISSION
 ↓
DELIVERY_STATE
 ↓
TRACKING
 ↓
FOLLOW_UP
 ↓
ESCALATION
 ↓
OUTCOME
 ↓
CLOSED / REOPENED
```

Transitions must be explicit and auditable.

## 4. Capability contract

Every registered capability should define at least:

- capability identifier;
- version;
- purpose;
- inputs;
- outputs;
- permissions;
- consent requirements;
- data sensitivity;
- dependencies;
- optional dependencies;
- fallback/degraded behavior;
- provenance requirements;
- owner;
- verification state;
- supported surfaces;
- completion tests.

## 5. Optionality rule

> Optional for the user does not mean optional for the ecosystem.

A capability can be declined by a user while remaining a supported ecosystem capability.

A capability must not be silently replaced by a different client or become an implicit dependency of an unrelated capability.

## 6. Dependency firewall

Required behavior:

```text
AI failure              → deterministic path
Government-search failure → truthful unavailable/stale state
Telegram failure        → other surfaces continue
Storage-provider failure → configured fallback/recovery path
Blockchain failure      → ordinary civic workflow continues
Agent failure            → guided/manual workflow
```

Optional technology may enhance a capability but must not create an unnecessary cascade failure.

## 7. Evidence and provenance

Facts supplied by the citizen, facts retrieved from authoritative sources, generated interpretations, and AI suggestions must remain distinguishable.

For authority/contact information:

```text
Candidate recipient
      ↓
Authoritative source lookup
      ↓
Freshness / verification state
      ↓
Citizen review
      ↓
Selected recipient
```

AI may assist with discovery or recommendation but must not fabricate official contact information.

## 8. External action boundary

Actions that create consequential external effects require an explicit authorization boundary.

Examples:

- official submission;
- sending a consequential message;
- publishing sensitive allegations;
- financial action;
- credential/signature operation;
- disclosure of protected information.

Agentic AI may prepare or propose such actions but cannot bypass required approval/policy gates.

## 9. Access-surface independence

Each surface must be independently operable within its supported scope.

Invalid dependency patterns include:

```text
Web → starts Telegram
Telegram → requires Web runtime
WhatsApp → requires Telegram
Android → requires Web process
DApp → requires Telegram
```

Valid pattern:

```text
Web ───────────────┐
Telegram ──────────┤
Mini App ──────────┤
Android ───────────┤
iOS ────────────────┤
WhatsApp ──────────┤
Messenger ─────────┤
DApp ──────────────┤
Future ────────────┘
          ↓
Shared capability contracts
```

## 10. AI invocation policy

AI should be selected because a capability benefits from it, not because a user happens to be on a particular channel.

Supported conceptual modes:

- deterministic/no AI;
- local AI;
- approved cloud AI;
- source-grounded RAG;
- controlled Agentic AI.

The routing decision must account for user preference, capability need, data sensitivity, policy and availability.

## 11. Storage/provider boundary

Domain and capability code must not depend directly on a provider-specific storage implementation.

```text
Capability
  ↓
Storage contract
  ├── Supabase adapter
  ├── SQL/local adapter
  ├── offline adapter where supported
  └── future decentralized adapter
```

Provider replacement must not require domain-model replacement.

## 12. Verification states

Capability status must distinguish:

```text
VISION
DESIGNED
IMPLEMENTED
FUNCTIONAL
TESTED
SECURITY_VERIFIED
PRIVACY_VERIFIED
PRODUCTION_READY
```

Documentation alone cannot promote a capability to a higher state.

## 13. Implementation rule

When an existing implementation already satisfies the contract, converge it into the canonical owner rather than creating a second framework.

When an implementation is historical or uncertain:

```text
identify
 → trace
 → archive if superseded
 → migrate consumers
 → verify
 → document
 → delete only when evidence permits
```

## 14. Acceptance criteria

This contract is operationally useful when:

- at least one complete Case lifecycle executes through Web;
- the same capability contracts can be invoked without Web-specific business logic;
- at least one non-Web surface consumes the same capability without depending on the Web runtime;
- AI can be disabled without breaking critical deterministic paths;
- provider failure is observable and isolated;
- consequential actions have explicit approval/policy gates;
- provenance and delivery state are truthful;
- tests cover normal and degraded paths.
