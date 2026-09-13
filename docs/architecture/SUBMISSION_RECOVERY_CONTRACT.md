# Submission Recovery Contract

**Status:** DESIGNED / INITIAL IMPLEMENTATION

## Purpose

Define restart-safe semantics for the boundary between Janavani and an
external submission destination.

## Canonical rule

A local process interruption while an external submission is in flight does
**not** prove success or failure. Janavani must represent that uncertainty
explicitly.

```text
created → submitting → unknown → reconcile → submitted | failed
```

`unknown` is a first-class local state. It is not an acknowledgement and is
not equivalent to `submitted`.

## Recovery rules

1. On restart, durable `submitting` records are discovered through the
   submission repository's `list_recoverable()` boundary.
2. Each interrupted record is converted to `unknown` without incrementing
   `retry_count`, because no new delivery attempt has occurred.
3. `unknown` records must be reconciled against an authoritative external
   status source before another delivery attempt is allowed.
4. Reconciliation may produce only `submitted` or `failed`.
5. A verified `submitted` result may carry an external reference.
6. A `failed` result is the only state made retryable by this contract.
7. A local timeout, exception, worker restart, or network disconnect alone
   must never produce a false `submitted` or `acknowledged` state.
8. Acknowledgement remains a separate evidence-backed capability; `submitted`
   is not acknowledgement.
9. Recovery mutations increment the durable submission version so restart
   processing is observable and compatible with later optimistic concurrency.

## Scope boundary

This contract does not define the external destination's status API, retry
backoff, queue implementation, or acknowledgement evidence schema. Those are
adapter/capability concerns.

It also does not activate PostgreSQL RLS, change production Supabase state, or
perform legacy-data migration.
