# Submission Idempotency and Concurrency Contract

**Status:** ACTIVE ARCHITECTURAL CONTRACT — initial implementation
**Scope:** Provider-neutral submission reservation, retry safety, and optimistic concurrency.

## Purpose

A submission is a consequential external operation. Persisting a submission record is not enough to prevent duplicate delivery when a caller retries after a timeout, process interruption, or unknown external outcome.

The canonical boundary is:

```text
SubmissionRequest
  -> stable idempotency_key
  -> atomic submission reservation
  -> submitting state
  -> external delivery
  -> CAS state transition
```

## Rules

1. Every externally initiated submission has a stable `idempotency_key`.
2. The key is persisted separately from `submission_id` and is unique.
3. Reusing a key with the same case, destination, document, and channel returns the original submission as an idempotent replay.
4. Reusing a key for a different operation is a terminal idempotency conflict.
5. `submitting` and `unknown` are not retry permission. An interrupted operation must be reconciled before another external attempt.
6. `failed` may be retried using the same idempotency key; the existing submission record is advanced with optimistic concurrency.
7. Every durable mutation increments `version` exactly once and uses compare-and-swap semantics.
8. A stale version is rejected; no blind overwrite is permitted on the consequential delivery path.
9. The external transport should propagate the stable submission identity/idempotency key whenever its protocol supports it. Janavani must not infer external success from local persistence.
10. `SUBMITTED` remains distinct from `ACKNOWLEDGED`; acknowledgement requires independent evidence/reference.

## Migration

The additive migration creates `idempotency_key`, backfills legacy rows from `submission_id`, makes the field non-null, and adds a unique index. It does not enable RLS, migrate legacy stores, or delete data.

## Provider boundary

The in-memory provider is a reference implementation. PostgreSQL implements the same contract with a unique idempotency index, transactional reservation, and version-qualified updates. Provider-specific SQL remains outside the domain contract.

## Verification gate

Before production delivery activation, demonstrate:

- same-key/same-operation replay;
- same-key/different-operation conflict;
- stale-version rejection;
- failed retry without a second submission record;
- interrupted `submitting` state cannot be retried without reconciliation;
- disposable PostgreSQL round-trip and concurrency tests;
- transport adapter behavior when an external protocol supports idempotency keys.

No production Supabase/RLS activation is implied by this contract.
