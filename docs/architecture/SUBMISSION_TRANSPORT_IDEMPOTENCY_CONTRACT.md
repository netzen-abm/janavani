# Submission Transport Idempotency Contract

**Status:** ACTIVE ARCHITECTURAL CONTRACT  
**Scope:** Provider-neutral delivery transport boundary used by `SubmissionCapability`  
**Date:** 13 September 2026

## Purpose

The canonical submission repository establishes durable submission identity and idempotency before an external side effect occurs. The delivery transport must receive that same stable identity so a provider adapter can participate in idempotent delivery whenever the destination protocol supports it.

The transport boundary must therefore preserve:

`SubmissionRequest → SubmissionRecord → DeliveryRequest → external delivery`

without generating a second transport-level identity that can diverge from the canonical submission.

## Canonical rules

1. Every `DeliveryRequest` carries both `submission_id` and `idempotency_key`.
2. `submission_id` identifies the canonical Janavani submission operation.
3. `idempotency_key` is the stable caller/request identity established by `SubmissionCapability` and persisted by the submission repository.
4. A delivery adapter MUST NOT silently replace either identifier with a newly generated operation key.
5. Provider adapters MAY translate the stable key into the destination protocol's native idempotency mechanism when one exists.
6. If a destination has no idempotency mechanism, the adapter must not falsely claim that transport delivery is exactly-once. Durable submission state and reconciliation remain authoritative.
7. `DeliveryReceipt` reports transport outcome only; it does not independently prove government acknowledgement.
8. `SUBMITTED` remains distinct from `ACKNOWLEDGED`.
9. Acknowledgement still requires independent evidence through the canonical evidence boundary.
10. The delivery contract remains provider- and surface-neutral; Telegram, Web, WhatsApp, mobile, DApp/Web3, and future channels are adapters rather than separate submission engines.

## Validation

`DeliveryRequest` rejects blank `submission_id`, `idempotency_key`, `case_id`, `document_id`, `destination_ref`, or `channel` values. This is a fail-closed contract check at the boundary before an adapter receives the request.

## Failure and retry semantics

The submission repository remains responsible for durable idempotency and optimistic concurrency. The transport adapter must not invent retry permission. In particular:

- `submitting` and `unknown` are not permission to issue an uncontrolled second delivery attempt;
- `failed` may be retried using the same canonical submission identity and idempotency key;
- the external transport should receive the stable key on every delivery attempt;
- an ambiguous external outcome requires reconciliation rather than an assumption of failure or success.

## Explicit non-goals

This contract does not activate:

- PostgreSQL RLS;
- production Supabase configuration;
- a provider-specific idempotency implementation;
- exactly-once delivery guarantees where the external protocol cannot provide them;
- atomic coupling of external transport with Case lifecycle persistence;
- Tool Gateway activation.

Those are separate architectural and production-readiness gates.

## Verification gate

The implementation must have tests proving:

- stable `idempotency_key` propagation from `SubmissionCapability` to `DeliveryRequest`;
- blank transport identity is rejected;
- the canonical submission repository remains the source of durable idempotency;
- provider adapters can receive the stable identity without depending on Janavani-specific transport types.
