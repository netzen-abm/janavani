# Submission + Case Atomic Orchestration — Implementation Gate

**Status:** IMPLEMENTATION SLICE — not production activation
**Date:** 14 September 2026

## Purpose

PR #142 established that durable Submission state and the corresponding Civic
Case lifecycle mutation must not be treated as independent successful writes
when they represent one local state transition. This slice implements the
provider-neutral boundary and a PostgreSQL transaction adapter for that rule.

## Atomic boundary

For coupled local mutations the adapter commits, in one PostgreSQL transaction:

1. Submission projection mutation.
2. Civic Case projection mutation.
3. Exactly one lifecycle event.

If any step fails, the transaction rolls back as one unit.

External delivery remains outside this database transaction. Therefore the
system still distinguishes database transaction certainty from external
transport certainty.

## Concurrency and idempotency

- Submission version is checked with compare-and-swap semantics.
- Case version is checked with compare-and-swap semantics.
- Lifecycle event ID is the idempotency key for the coupled local operation.
- Reusing an event ID with a different event shape is rejected.
- The Submission idempotency key remains immutable and is not repurposed as a
  lifecycle event identifier.
- A replay returns the already committed Submission and Case versions rather
  than applying the mutation twice.

## Failure/restart semantics

The boundary is intentionally local and deterministic. A process interruption
before commit leaves no partial local mutation. A process interruption after
commit leaves a durable pair that can be read and reconciled. External delivery
is still reconciled separately when its outcome is unknown.

## Explicit non-goals

This slice does not:

- enable PostgreSQL RLS;
- activate Supabase production RPCs;
- move binary evidence or document content into PostgreSQL;
- make external government delivery part of a database transaction;
- weaken authorization, consent, or approval requirements;
- remove the existing compatibility repository APIs.

## Activation gate

Before wiring this adapter into production capability execution, the repository
must add disposable-PostgreSQL integration coverage for rollback, exact replay,
idempotency conflict, stale Case writer, stale Submission writer, concurrent
mutation convergence, and restart/unknown-outcome recovery. Production schema
and RLS remain separately gated by the canonical PostgreSQL contracts.
