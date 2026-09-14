# Janavani — Submission ↔ Case Orchestration Contract

**Status:** DESIGNED / IMPLEMENTATION GATE — no production activation authorized  
**Scope:** Durable coordination between `civic_case_submissions` state and the Civic Case lifecycle projection

## 1. Purpose

The submission capability now has durable submission idempotency, optimistic concurrency, explicit `unknown` outcomes, and provider-neutral reconciliation. The remaining high-value integrity gap is the boundary between the durable Submission mutation and the related Civic Case lifecycle mutation.

Today these are separate persistence operations. A successful Submission CAS mutation can therefore be committed while the subsequent Case transition fails, and a Case transition can be committed independently of a corresponding Submission mutation. The architecture must not imply that these two durable states are atomic when they are not.

This contract makes that boundary explicit and defines the next bounded implementation slice.

## 2. Current safe sequence

External delivery cannot be made atomic with PostgreSQL. The intended durable sequence is:

```text
authorize
  -> validate consent / ownership / document / destination
  -> atomically persist Submission attempt + Case SUBMITTING lifecycle mutation
  -> perform external transport
  -> atomically persist Submission outcome + corresponding Case lifecycle mutation
  -> independently evidence acknowledgement
```

The external transport remains outside the database transaction.

## 3. Required atomic units

### 3.1 Begin submission

The first delivery attempt must atomically persist:

- Submission `created/submitting` state and attempt identity;
- Case `READY → SUBMITTING` projection;
- the corresponding immutable Case lifecycle event;
- the expected-version checks for both aggregates;
- stable idempotency identity.

A failed transaction must leave both durable aggregates unchanged.

### 3.2 Final transport outcome

For a known `submitted` or `failed` transport outcome, the corresponding Submission and Case mutations must be committed as one database transaction where both records must change.

For an `unknown` outcome, the Submission must become `unknown` durably. The Case remains `SUBMITTING`; no false success transition is allowed.

### 3.3 Reconciliation

For an independently observed `unknown → submitted`, the Submission and Case `SUBMITTED` transition should be committed atomically. If the observation is `unknown → failed`, only the Submission needs to change; the Case must remain non-submitted.

## 4. Provider-neutral boundary

The domain contract must not expose PostgreSQL, Supabase, Psycopg, RPC names, or provider-specific transaction objects.

Conceptual operations:

```text
begin_submission_mutation(
    submission,
    expected_submission_version,
    case_projection,
    expected_case_version,
    lifecycle_event,
    idempotency_key
) -> mutation_result
```

```text
finalize_submission_mutation(
    submission,
    expected_submission_version,
    case_projection_or_none,
    expected_case_version_or_none,
    lifecycle_event_or_none,
    idempotency_key
) -> mutation_result
```

```text
reconcile_submission_mutation(
    submission,
    expected_submission_version,
    case_projection_or_none,
    expected_case_version_or_none,
    lifecycle_event_or_none,
    idempotency_key
) -> mutation_result
```

The exact repository interface and PostgreSQL function/RPC shape remain implementation decisions after schema verification.

## 5. Idempotency

A submission idempotency key is not sufficient by itself to deduplicate a Case lifecycle event. Each atomic mutation must have a stable mutation/event identity and must reject materially different payloads under the same identity.

Replaying an already committed mutation must return the committed result without advancing either version twice.

## 6. Concurrency

Both durable versions are part of the mutation precondition:

```text
submission.version == expected_submission_version
AND
case.version == expected_case_version
        │
        ├── yes → commit both mutations atomically
        └── no  → reject; commit neither
```

A stale writer must never overwrite the newer Submission or Case projection.

## 7. Unknown database outcome

A database connection loss during commit is not evidence of rollback. The caller must not manufacture `failed`, `submitted`, or `acknowledged` merely because the client did not receive a response.

Recovery requires deterministic observation of durable state using stable mutation identity.

This database uncertainty is distinct from external transport uncertainty:

- **database unknown:** did the local transaction commit?
- **transport unknown:** did the destination accept the submission?

They must never be conflated.

## 8. Acknowledgement boundary

`SUBMITTED` means the submission outcome has been established. It does not mean the government acknowledged receipt.

`ACKNOWLEDGED` remains evidence-backed and independent. The orchestration transaction must not fabricate acknowledgement from a transport receipt unless the receipt itself satisfies the independent acknowledgement evidence contract.

## 9. Implementation constraints

The next implementation must:

- reuse the existing canonical Case transaction boundary rather than create a second competing Case transaction model;
- reuse the existing Submission idempotency/CAS semantics;
- preserve the provider-neutral capability layer;
- use one verified PostgreSQL transaction boundary for multi-table mutation;
- keep external transport outside the transaction;
- preserve `unknown` as a first-class outcome;
- preserve archive-first and migration-gated rules;
- add disposable PostgreSQL integration tests before production consideration.

It must not:

- activate RLS;
- activate production Supabase/Render database configuration;
- add provider-specific logic to capabilities;
- claim exactly-once external delivery;
- infer acknowledgement;
- perform a broad repository rewrite.

## 10. Required verification gate

Before production adoption, tests must prove:

1. Begin submission commits Submission + Case + lifecycle event together.
2. Case mutation failure rolls back Submission mutation.
3. Submission mutation failure rolls back Case mutation/event.
4. Final `submitted` outcome commits both durable mutations together.
5. `failed` outcome never advances Case to `SUBMITTED`.
6. `unknown` outcome leaves Case `SUBMITTING` and remains reconcilable.
7. Reconciliation `submitted` commits Submission + Case transition atomically.
8. Stale Submission version changes neither aggregate.
9. Stale Case version changes neither aggregate.
10. Concurrent mutation permits only one valid expected-version commit.
11. Replayed mutation does not duplicate Case events or advance versions twice.
12. Conflicting mutation identity is rejected.
13. Database interruption does not manufacture success.
14. Restart/recovery can determine committed state from durable mutation identity.
15. Acknowledgement remains independent and evidence-backed.

## 11. Decision

**Approved as the next bounded architectural implementation slice.**

The current separate Submission and Case writes remain valid development behavior but are **not atomic**. No caller, adapter, or documentation may represent them as one transaction until this contract's implementation and verification gate are complete.
