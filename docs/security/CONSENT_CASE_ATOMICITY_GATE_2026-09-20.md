# Consent + Case Atomicity Gate

The canonical consent capability now supports an injected `ConsentCaseAtomicRepository`.
When supplied, the capability builds the final consent + Case projection in memory
and persists both through one Unit of Work. The PostgreSQL adapter uses the same
transaction and binds `janavani.principal_id` before writes.

## Required invariants

1. Consent subject equals the authenticated principal.
2. The Case already belongs to that principal through the normal capability boundary.
3. The Case references the consent before persistence.
4. Consent INSERT/UPDATE and Case UPDATE share one PostgreSQL transaction.
5. The Case version is checked with optimistic concurrency.
6. The lifecycle event is inserted in the same transaction.
7. Any failure rolls back Consent, Case and event together.
8. A second request must remain idempotent at the capability/API layer; the atomic repository itself is intentionally a persistence boundary, not an idempotency policy engine.

## Current limitation

The atomic adapter currently covers the consent + Case projection + consent event.
It does not perform external submission side effects. Those remain behind the
Submission capability and its existing atomic submission transaction.

## Production gate

Do not activate production RLS until integration tests prove:

- rollback when Case update fails after Consent write;
- rollback when event insert fails;
- stale Case version rejects the transaction;
- cross-user principal cannot write Consent or Case;
- successful transaction persists all three records;
- repeated operation does not create an inconsistent consent/case state.