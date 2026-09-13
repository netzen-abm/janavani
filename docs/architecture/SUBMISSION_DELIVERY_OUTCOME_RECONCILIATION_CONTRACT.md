# Submission Delivery Outcome & Reconciliation Contract

**Status:** ACTIVE ARCHITECTURAL CONTRACT  
**Scope:** Provider-neutral delivery outcome semantics between `SubmissionCapability` and external delivery adapters  
**Date:** 13 September 2026

## Purpose

Janavani must never convert an ambiguous external delivery result into a false success or a false failure. The canonical submission identity already survives retries through `submission_id` and `idempotency_key`. This contract defines what the delivery boundary is allowed to say about the external side effect.

The canonical progression is:

`created → submitting → submitted | unknown | failed → acknowledged`

`unknown` is an explicit durable state. It is not a synonym for `failed`, and it is not permission to retry.

## Provider-neutral delivery outcomes

`DeliveryReceipt.outcome` has exactly three transport-level meanings:

- `submitted`: the adapter has sufficient evidence to report that the destination accepted the delivery operation. This does **not** prove government acknowledgement.
- `unknown`: the adapter cannot establish whether the destination accepted the operation. The caller must reconcile before another delivery attempt.
- `failed`: the adapter has sufficient evidence that the delivery operation failed and may be retried under the canonical submission idempotency contract.

A receipt does not directly transition a Case to `ACKNOWLEDGED`. Acknowledgement requires independent acknowledgement evidence through the canonical evidence boundary.

## Exception semantics

A transport exception after external delivery may have begun is ambiguous by default. Generic exceptions raised by `DeliveryTransport.deliver()` therefore become durable `unknown` state at the submission boundary.

A provider adapter may raise `DeliveryTransportError(outcome=DeliveryOutcome.FAILED)` only when it has reliable evidence that the operation failed before creating an externally accepted submission. `DeliveryTransportError(outcome=DeliveryOutcome.UNKNOWN)` is the explicit ambiguous form.

Adapters must not use `failed` merely because a local timeout, connection reset, process restart, or client-side exception occurred after an external side effect could have started.

## Durable state rules

1. `submitting` means an external attempt is in progress or its completion is not yet locally established.
2. `unknown` means the completion outcome cannot safely be inferred locally.
3. `unknown` must preserve the same `submission_id` and `idempotency_key`.
4. Transition to `unknown` does not increment `retry_count` because no second attempt occurred.
5. `unknown` is not retry permission.
6. Reconciliation may establish `submitted` or `failed` only from an independent, provider-supported observation.
7. `failed` increments retry accounting when a delivery attempt is definitively failed.
8. A successful transport result may transition the submission to `submitted`; it must not silently infer `acknowledged`.
9. Acknowledgement remains a separate evidence-backed operation.
10. No provider may invent exactly-once guarantees when its destination protocol cannot support them.

## Reconciliation boundary

The existing provider-neutral recovery contract remains authoritative for `unknown` submissions. Reconciliation must establish an externally supported outcome before retry permission is granted.

The canonical identity remains stable through reconciliation and any later retry:

`submission_id + idempotency_key`

A reconciliation mechanism may use a provider-native receipt, destination lookup, delivery status API, verified acknowledgement evidence, or another explicitly trusted observation source. The specific provider mechanism is outside this contract.

## Case lifecycle boundary

Transport outcome and Case lifecycle remain separate boundaries:

- `submitted` is not `acknowledged`;
- `unknown` must not move the Case to `SUBMITTED`;
- transport success does not prove a government response;
- acknowledgement requires independent evidence;
- external delivery is not atomically coupled to Case lifecycle persistence by this contract.

This preserves truthful civic state even when an external system is unavailable or ambiguous.

## Non-goals

This contract does not activate:

- provider-specific transport adapters;
- exactly-once delivery guarantees;
- PostgreSQL RLS;
- production database configuration;
- Tool Gateway;
- atomic coupling of external transport and Case lifecycle persistence;
- a provider-specific reconciliation service.

## Verification gate

Before production delivery activation, tests must prove:

- explicit `unknown` receipts persist `unknown` and do not mark the Case submitted;
- ambiguous transport exceptions persist `unknown` rather than `failed`;
- explicit failed outcomes remain retryable;
- `unknown` does not increment retry count;
- stable submission identity remains intact;
- `submitted` remains distinct from `acknowledged`;
- existing idempotency and optimistic-concurrency contracts continue to hold.
