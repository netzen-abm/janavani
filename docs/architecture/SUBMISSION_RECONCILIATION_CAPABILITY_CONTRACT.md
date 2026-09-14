# Submission Reconciliation Capability Contract

**Status:** ACTIVE ARCHITECTURAL CONTRACT — PROVIDER-NEUTRAL CAPABILITY
**Date:** 14 September 2026

## Purpose

This contract defines the shared capability for resolving a durable `unknown` submission outcome. It prevents a timeout, restart, or ambiguous transport exception from becoming an unsafe retry or false success.

## Canonical boundary

`Identity → Authorization → Unknown Submission → Independent Observation Source → CAS Submission Mutation → Case Lifecycle (only for confirmed submitted)`

The observation source is an adapter boundary. It may use a provider status API, destination lookup, verified delivery receipt, or another explicitly trusted observation mechanism. This capability does not contain provider-specific transport logic.

## Rules

1. Only `unknown` submissions are eligible for reconciliation.
2. Reconciliation requires the caller to be authorized for the submission capability.
3. The submission remains bound to its original `submission_id` and `idempotency_key`.
4. The observation source must return either `submitted` or `failed` and must provide a source reference and observation timestamp.
5. The durable submission mutation uses optimistic concurrency; a stale reconciler must fail rather than overwrite a newer state.
6. `submitted` is persisted before the Case is advanced to `SUBMITTED`.
7. `failed` is persisted without advancing the Case to `SUBMITTED`; the submission can subsequently enter the existing retry path.
8. Reconciliation never creates government acknowledgement. `acknowledged` remains an independent evidence-backed state.
9. Reconciliation does not retry external delivery.
10. Provider adapters must not claim exactly-once semantics unless their destination protocol actually supports them.

## Authorization

The capability uses the canonical authorization boundary and resource-scopes the decision to the submission being reconciled. Cross-principal Case ownership remains enforced by the Case capability.

## Concurrency

The reconciler reads an `unknown` SubmissionRecord, obtains an independent observation, then performs `update_if_version(..., expected_version=<observed version>)`. Concurrent reconciliation therefore cannot silently overwrite another successful mutation.

## Case lifecycle boundary

A confirmed `submitted` observation may advance a Case from `SUBMITTING` or `QUEUED` to `SUBMITTED`. A confirmed `failed` observation never advances the Case to `SUBMITTED`.

This contract intentionally does not couple the submission mutation and Case lifecycle mutation into one database transaction. That is a separate architectural slice and must not be implied by this capability.

## Non-goals

This contract does not activate:

- provider-specific reconciliation adapters;
- automatic retry of unknown outcomes;
- PostgreSQL RLS;
- production database configuration;
- Tool Gateway;
- exactly-once external delivery;
- automatic acknowledgement inference;
- atomic Case + Submission persistence.

## Verification gate

Before production use, tests must prove:

- only unknown submissions reconcile;
- authorization and Case ownership are enforced;
- submitted observation preserves identity and advances the Case exactly once;
- failed observation leaves the Case non-submitted and makes the submission retryable;
- stale reconciliation is rejected by optimistic concurrency;
- provider observation failures do not fabricate an outcome;
- acknowledgement remains separate.
