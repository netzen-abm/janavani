# Submission Schema Convergence Contract

**Status:** ACTIVE ARCHITECTURAL CONTRACT — compatibility adapter aligned
**Scope:** `civic_case_submissions` persistence used by the canonical submission capability.

## Decision

The checked-in canonical PostgreSQL/Supabase migration is the schema authority for `civic_case_submissions`. The PostgreSQL submission repository may retain a compatibility initializer for standalone/test deployments, but that initializer must mirror the canonical schema and must not create a divergent schema.

The canonical persisted fields are:

```text
submission_id
case_id
 destination_ref
document_ref
channel
state
attempted_at
submitted_at
acknowledged_at
external_reference
ack_ref
error_code
retry_count
version
created_at
updated_at
```

Temporal fields use `TIMESTAMPTZ`; `version` is `BIGINT`; `case_id` references `civic_cases(case_id)`.

## Recovery

`submitting` is the only restart-recoverable state. Recovery does not infer success or failure. An interrupted record becomes `unknown`, and an unknown record requires independent reconciliation before retry.

## Boundary

- Production schema changes belong in versioned migrations.
- The repository does not activate RLS.
- The repository does not infer acknowledgement from local submission state.
- Submission idempotency remains a separate capability concern and must not be approximated by a blind upsert when an external operation is being retried.
- Existing data is not migrated or deleted by this convergence change.
