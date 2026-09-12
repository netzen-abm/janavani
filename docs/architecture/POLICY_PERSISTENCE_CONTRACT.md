# Policy Persistence Contract

**Status:** DESIGNED / INITIAL REFERENCE ADAPTER  
**Version:** 1.0  
**Date:** 12 September 2026

## Purpose

This contract defines the persistence boundary for composed authorization policy state.

The repository stores policy inputs; it does not decide authorization. The canonical authorization kernel and policy-composition layer remain the decision boundaries.

## Policy families

Durable policy state may include:

1. **Delegation grants** — grantor, delegate, bounded capabilities/actions/resources, expiry, and revocation state.
2. **Consent** — subject, purpose, scope, status, expiry/revocation and proof reference.
3. **Service-identity policy** — explicit capability/action allow-lists for service principals.

## Boundary

```text
Interface / Adapter
        ↓
Identity + Authentication
        ↓
Canonical Authorization Kernel
        ↓
Policy Composition
        ↓
Policy Repository  ← this contract
        ↓
Provider Adapter (PostgreSQL / future provider)
```

The repository must not:

- infer authorization from storage presence;
- grant capabilities that the canonical authorization model does not permit;
- bypass delegation, consent, or service-policy gates;
- expose provider-specific types to domain callers;
- activate PostgreSQL RLS implicitly;
- delete revoked policy state merely because it is inactive.

## Repository contract

The provider-neutral repository supports deterministic operations for:

- save/get delegation;
- list delegations for a delegate;
- save/get consent;
- list consents for a subject;
- save/get service-identity policy.

Implementations may add provider-specific transactions, indexes, optimistic concurrency, or retention mechanisms behind the contract.

## Security invariants

- Missing policy state is not permission.
- Revocation is durable policy state and must remain auditable.
- Expiry is evaluated against a trusted current time; persisted expiry must not be silently rewritten by reads.
- Delegation remains bounded by grantor, delegate, capability, action, resource and expiry/revocation state.
- Consent remains bound to its subject, purpose and scope.
- Service credentials require explicit service policy; authentication alone is insufficient.
- Repository lookup scope must not permit cross-principal enumeration through an application-level convenience method.
- Provider adapters must preserve immutable domain semantics.

## Reference implementation

`InMemoryPolicyRepository` is a deterministic reference adapter for tests and local development. It is not a production persistence implementation and does not activate database authorization.

## PostgreSQL/RLS gate

PostgreSQL persistence must be implemented only after:

1. policy schema ownership is explicitly assigned;
2. transaction semantics are defined;
3. authorization-to-RLS alignment is verified;
4. negative access tests pass;
5. revocation/expiry behavior is tested;
6. cross-principal enumeration is denied;
7. audit/provenance requirements are defined.

## Delegated consent

A delegated consequential operation may use consent belonging to the grantor/resource owner when the composed request explicitly identifies that consent subject and the delegation authorizes the delegate for the same bounded capability/action/resource. Ordinary non-delegated execution continues to use the executing principal as the default consent subject.

## Non-goals

This contract does not define:

- citizen login;
- authentication provider selection;
- PostgreSQL schema or RLS SQL;
- capability gateway/tool execution;
- evidence storage;
- application-specific policy configuration UI.
