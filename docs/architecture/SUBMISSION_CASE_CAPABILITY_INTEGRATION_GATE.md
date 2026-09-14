# Submission–Case Capability Integration Gate

**Status:** IMPLEMENTATION GATE — not production activation authorization

## Purpose

The atomic Submission–Case persistence boundary is now present on `main`. The next bounded layer is to replace the coupled local write sequences inside `SubmissionCapability` and `SubmissionReconciliationCapability` with that boundary without changing authorization, consent, delivery, acknowledgement, or recovery semantics.

## Required invariant

For every coupled local mutation:

```text
authorize
→ validate
→ ATOMIC LOCAL TRANSACTION
   [Submission projection + Case projection + exactly one lifecycle event]
→ external transport / independent observation
→ ATOMIC OUTCOME TRANSACTION
   [Submission outcome + Case outcome]
```

External transport remains outside the database transaction. Unknown external outcomes must remain unknown and must never be converted into success.

## Integration rules

1. Do not weaken or bypass the canonical authorization kernel.
2. Do not make consent implicit; existing explicit consent requirements remain unchanged.
3. Submission idempotency keys remain immutable operation identity and must not be conflated with lifecycle event IDs.
4. Each coupled local mutation receives its own deterministic/stable lifecycle event identity suitable for idempotent replay.
5. The first submission attempt must atomically persist `Submission=submitting` with the Case transition `READY → SUBMITTING`.
6. A failed retry must not repeat `begin_submission`; it resumes external delivery from the durable `SUBMITTING` state.
7. A verified `SUBMITTED` outcome must atomically persist the Submission outcome and Case `SUBMITTED` lifecycle event.
8. A verified acknowledgement must atomically persist the Submission acknowledgement and Case acknowledgement event.
9. Reconciliation of an unknown outcome must atomically converge Submission and Case when the independent observation proves submission; a failed observation must not falsely advance the Case.
10. Optimistic concurrency failures must leave both projections unchanged.
11. Idempotent replay must not append a duplicate lifecycle event or advance either version again.
12. RLS and production provider activation remain separately gated.

## Required tests before merge

### Submission capability

- first attempt: atomic `SUBMITTING` mutation
- stale Case writer: entire local mutation rejected
- stale Submission writer: entire local mutation rejected
- local transaction rollback: neither projection nor event survives
- exact replay: no duplicate event/version advance
- conflicting event identity: fail closed
- failed retry resumes delivery without repeating Case `begin_submission`
- external `UNKNOWN`: durable unknown Submission and Case remains `SUBMITTING`
- external `FAILED`: durable failed Submission and retry semantics preserved
- external `SUBMITTED`: atomic Submission + Case outcome
- acknowledgement evidence: atomic Submission acknowledgement + Case acknowledgement

### Reconciliation capability

- unknown → submitted: atomic Submission + Case convergence
- unknown → failed: Submission failure persisted; Case remains `SUBMITTING`
- stale writer: no partial update
- exact replay: no duplicate lifecycle event
- cross-principal access remains denied
- restart/recovery after an ambiguous database outcome does not claim false success

## Explicit non-goals

This gate does not authorize:

- PostgreSQL RLS activation
- production migration execution
- external transport inside the database transaction
- Tool Gateway implementation
- authorization-policy redesign
- a second Submission or Case persistence path

## Verification checkpoint

The first exact-head PR run exposed eight functional failures. The failures were traced to the initial integration branch behavior around the existing non-atomic compatibility path; the corrected branch preserves the legacy development/test path while activating the atomic boundary only when explicitly injected. The next exact-head run is authoritative for functional verification.
