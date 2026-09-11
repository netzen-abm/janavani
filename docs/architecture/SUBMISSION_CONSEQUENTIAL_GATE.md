# Submission Consequential Gate

## Purpose

Submission is the first high-risk civic side effect migrated to the shared Consequential Operation Gate.

The Submission capability remains the domain authority for submission invariants and transport execution. The shared gate decides whether the consequential operation may proceed.

```text
Authenticated Identity
        ↓
Execution Context
        ↓
Authorization
        ↓
Execution-aware Consent
        ↓
Explicit User Approval
        ↓
Submission Capability
        ↓
Delivery / Transport Side Effect
```

## Enforced controls

A submission requires:

1. authenticated identity owning the Case;
2. an execution context bound to `case:submit` and the Case resource;
3. capability authorization;
4. consent for `case_submission` and the requested destination scope;
5. explicit user approval;
6. idempotency for the external side effect;
7. an attached document and valid destination;
8. approved artifact resolution when the delivery transport is used.

Missing or invalid consent cannot be replaced by explicit approval. Authorization denial cannot be overridden by consent or approval.

## Scope boundary

This migration changes only the Submission capability. Other consequential capabilities remain on their existing boundaries until separately migrated and tested. The gate does not execute transport operations and does not make delivery providers authoritative.
