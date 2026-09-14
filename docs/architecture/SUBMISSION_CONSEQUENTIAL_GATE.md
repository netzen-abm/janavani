# Submission Consequential Gate

## Purpose

Submission is a high-risk civic side effect governed by the shared Consequential Operation Gate.

The Submission capability remains the domain authority for submission invariants, idempotency, delivery outcome handling, reconciliation, and transport execution. The shared gate decides whether the consequential operation may proceed.

```text
Authenticated Identity
        ↓
Execution Context
        ↓
Shared Consequential Gate
   ├── Authorization
   ├── Consent
   └── Explicit Approval
        ↓
Submission Capability
        ↓
Delivery / Transport Side Effect
```

## Enforced controls

A submission requires:

1. an authenticated identity owning the Case;
2. an execution context bound to `case:submit` and the Case resource when supplied;
3. capability authorization;
4. consent for `case_submission` and the requested destination scope;
5. explicit user approval because submission is a consequential external side effect;
6. an idempotency key for the external operation;
7. an attached document and valid destination;
8. an approved artifact when the delivery transport is used.

Authorization denial cannot be overridden by consent or approval. Missing consent cannot be replaced by approval.

## Scope boundary

This migration changes only the Submission capability. The gate does not execute transport operations and does not make a delivery provider authoritative. Other consequential capabilities remain on their existing boundaries until separately migrated and tested.
