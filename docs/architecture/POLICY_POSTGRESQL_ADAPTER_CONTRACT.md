# Policy PostgreSQL Adapter Contract

**Status:** CONTROLLED IMPLEMENTATION
**Scope:** Durable persistence adapter for composed authorization policy inputs

## Boundary

```text
Canonical authorization kernel
        ↓
Policy composition
        ↓
PolicyRepository
        ↓
PostgresPolicyRepository
        ↓
PostgreSQL
```

The adapter implements the existing provider-neutral repository contract. Storage presence never grants authority; evaluation remains in the authorization layers.

## Persisted policy families

- `janavani_delegation_grants`: bounded grantor/delegate capability, action and resource scope, expiry and revocation.
- `janavani_policy_consents`: purpose/scope-bound consent state, including expiry, revocation and proof reference.
- `janavani_service_identity_policies`: explicit service-principal capability/action allow-lists.

These names are intentionally separate from the Civic Case tables. Policy state is shared infrastructure and may be referenced by multiple surfaces and capabilities.

## Adapter rules

1. Use parameterized SQL only.
2. Preserve opaque principal and resource identifiers without reinterpretation.
3. Preserve revoked and expired state; reads do not delete or rewrite policy.
4. Scope list operations by the requested principal/subject.
5. Return provider-neutral domain objects only.
6. Keep RLS disabled/not introduced by this adapter.
7. Keep authorization decisions outside persistence.
8. Use transactions for individual writes so partial policy rows are not committed.
9. Do not synthesize consent or delegation records.

## RLS gate

This adapter is not a declaration that production RLS is ready. RLS requires the separate authorization matrix, identity mapping, database-visible principal context, negative tests, audit semantics, and rollback/recovery evidence.

## Production gate

Controlled implementation requires a real disposable PostgreSQL integration run. Production activation additionally requires restart durability, backup/restore, outage behavior, concurrency/idempotency evidence, privacy/retention review, and alignment with the canonical RLS contract.
