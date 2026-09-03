# Janavani — Canonical Civic Case Transaction Contract

**Status:** DESIGN / IMPLEMENTATION GATE — no production database mutation authorized
**Scope:** Atomic persistence of Civic Case aggregate projection and lifecycle events

## 1. Purpose

The current Supabase provider deliberately stops short of claiming multi-table atomicity. This contract defines the boundary required before the provider can become the production durable case implementation.

The contract is provider-neutral at the domain boundary. PostgreSQL/Supabase may implement it through a stored function/RPC or another verified transaction mechanism, but application code must not depend on a sequence of independent table writes for one domain mutation.

## 2. Atomic unit

For a domain mutation that changes both the case projection and its lifecycle event, the database operation is one atomic unit:

```text
authorize
  -> validate transition
  -> call atomic persistence boundary
       ├── verify case exists / does not exist
       ├── verify expected version
       ├── apply case projection
       ├── append lifecycle event
       └── advance version
  -> return persisted version/result
```

If any step fails, none of the case projection or event changes are committed.

## 3. Required operation

Conceptual operation:

```text
persist_civic_case_mutation(
    case_id,
    expected_version,
    case_projection,
    lifecycle_event,
    idempotency_key
) -> persistence_result
```

The exact SQL function name and argument types remain implementation decisions after schema verification.

## 4. Preconditions

The transaction boundary must enforce:

- valid case identifier;
- expected version for an existing case;
- event belongs to the same case;
- event ID is an idempotency key;
- requested new version is expected version plus one;
- duplicate events are not silently appended;
- structural database constraints are satisfied.

Domain lifecycle rules remain owned by the application/domain layer. The transaction boundary provides persistence integrity and concurrency protection; it does not become the lifecycle state machine.

## 5. Idempotency

Retries must be deterministic.

If the same event ID/idempotency key has already committed for the same case and operation, the boundary must return the existing committed result rather than append another lifecycle event or advance the case twice.

If the same idempotency key is presented with materially different payload, the operation must fail rather than silently reinterpret the request.

## 6. Optimistic concurrency

For an existing case:

```text
current version == expected version
        │
        ├── yes → apply mutation and advance version atomically
        └── no  → reject as stale; make no changes
```

The repository must surface stale-version rejection as its existing concurrency error.

## 7. Create operation

Creation may use a separate atomic operation:

```text
create_civic_case(
    case_projection,
    lifecycle_event,
    idempotency_key
) -> persistence_result
```

It must create the case at version `1` and append its initial lifecycle event in the same transaction.

A repeated create request must be idempotent by its agreed creation key/case identity and must not create a second aggregate accidentally.

## 8. References

Evidence and document reference rows that are part of the same domain mutation must be included in the same transaction when their addition is semantically part of that mutation.

Consent records remain owned by the consent capability. The case transaction may reference consent state but must not fabricate, extend, or revoke consent.

## 9. External submission is not one transaction

External government delivery cannot be made atomic with PostgreSQL.

The safe sequence is:

```text
authorize
  -> validate current consent
  -> atomically persist submission attempt
  -> perform external transport
  -> atomically persist transport outcome
  -> persist acknowledgement only when independently evidenced
```

A transport timeout remains an uncertain outcome. The system must not convert uncertainty into `ACKNOWLEDGED`.

## 10. Failure semantics

The implementation must distinguish at least:

- validation failure;
- stale version;
- duplicate idempotency key with same payload;
- idempotency conflict with different payload;
- database constraint failure;
- database unavailable/timeout;
- unknown transaction outcome.

Unknown transaction outcome must not be represented as successful lifecycle transition unless the committed result can be deterministically recovered.

## 11. Required tests

Before production adoption, tests must demonstrate:

1. case + event commit together;
2. case update failure rolls back the event;
3. event insert failure rolls back the case projection;
4. stale version changes neither projection nor event history;
5. repeated identical idempotency request does not duplicate the event;
6. conflicting idempotency payload is rejected;
7. concurrent writers permit only one expected-version mutation;
8. create persists version `1` and its initial event atomically;
9. database interruption does not manufacture success;
10. restart preserves committed state;
11. submission timeout remains distinguishable from acknowledgement;
12. acknowledgement requires evidence and cannot be fabricated by a citizen/client.

## 12. Verification gate

Do not activate a production RPC/function until the actual target PostgreSQL/Supabase schema has been inspected and reconciled with:

- `docs/architecture/CANONICAL_CASE_POSTGRES_SCHEMA.md`;
- `docs/architecture/CIVIC_CASE_DATABASE_CONTRACT.md`;
- `docs/architecture/CANONICAL_CASE_RLS_AUTHORIZATION_MATRIX.md`;
- `planning/IDENTITY_ACCESS_TRUST_CONTRACT.md`;
- `src/core/civic_case.py`.

The repository provider may remain available for development/testing, but it must continue to document that its current multi-table writes are not atomic until this gate is passed.

## 13. Decision

**Approved as the transaction design boundary.**

This document authorizes no production schema change, no RLS activation, no data migration, and no deployment. Those remain separately gated by verified evidence.
