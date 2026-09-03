# Supabase Civic Case Transaction Contract

**Status:** REQUIRED BEFORE PRODUCTION CASE PERSISTENCE

## Purpose

The canonical Civic Case repository now has a Supabase/PostgreSQL provider, but its current implementation deliberately does not claim multi-table atomicity. This document defines the database transaction boundary required before that provider can become the production repository.

No production database mutation is authorized by this document.

## Transaction boundary

A single logical Civic Case write must be committed atomically across the case aggregate and its owned relational records:

1. `civic_cases`
2. `civic_case_events`
3. `civic_case_evidence_refs`
4. `civic_case_document_refs`
5. `civic_case_audit` when an audit record is required by policy

Consent records remain owned by the consent capability. Submission records remain governed by the submission/delivery capability. A case write must never manufacture consent or government acknowledgement.

The transaction must satisfy:

- all-or-nothing commit;
- rollback on any child-write failure;
- optimistic version checking;
- idempotent event insertion;
- idempotent reference insertion;
- no partial case aggregate after a failed request;
- deterministic retry behavior;
- historical event immutability;
- no fabricated acknowledgement state.

## Recommended RPC boundary

The production provider should call one verified PostgreSQL function/RPC for a logical case persistence operation rather than issuing independent client-side table writes.

Conceptual operation:

`persist_civic_case(case_payload, expected_version, idempotency_key, actor_context)`

The exact PostgreSQL signature is implementation-specific and must be finalized only after the live schema and RLS model are verified.

### Required RPC behavior

For a new case:

1. validate the case identifier and canonical enum values;
2. validate actor authorization in the database boundary where required;
3. insert the case at version `1`;
4. insert only new case events;
5. insert/upsert only permitted evidence/document references;
6. write the corresponding audit record when required;
7. commit once;
8. return the persisted case version and outcome.

For an existing case:

1. lock or conditionally update the case using `case_id + expected_version`;
2. reject a stale version without modifying any child records;
3. advance the version exactly once;
4. insert only events not already accepted under the idempotency rules;
5. upsert references under stable uniqueness constraints;
6. write the corresponding audit record when required;
7. commit once;
8. return the new version and outcome.

## Idempotency

Every externally retriable write must carry an idempotency key or an equivalent stable event identifier.

At minimum:

- `event_id` must be unique per case;
- reference uniqueness must prevent duplicate case/evidence/document relationships;
- the same idempotency key must not create a second logical state transition;
- a retry after a committed request must return the previously committed outcome rather than replaying the transition.

## Concurrency

The application currently uses an optimistic version field on `CivicCase`.

Required invariant:

`UPDATE ... WHERE case_id = :case_id AND version = :expected_version`

must affect exactly one case row for a successful update.

A zero-row update is a concurrency conflict and must cause the complete logical operation to fail without child-row side effects.

## Error semantics

The provider must distinguish at least:

- validation failure;
- authorization failure;
- consent/policy failure;
- stale-version conflict;
- idempotent replay;
- persistence/transaction failure;
- unavailable database/provider.

The API layer must not translate persistence success into government acknowledgement. `SUBMITTED` and `ACKNOWLEDGED` remain distinct lifecycle facts.

## RLS interaction

The RPC must be designed together with the approved RLS authorization matrix. It must not become a privilege-escalation bypass.

Required verification includes:

- citizen A cannot write citizen B's case;
- revoked/inactive delegates cannot write;
- destination services cannot access unrelated cases;
- anonymous callers cannot enumerate cases;
- case writes cannot fabricate acknowledgement;
- historical events cannot be updated or deleted through the case path;
- stale-version writes fail closed;
- service credentials are scoped to their intended capability.

## Verification gate

Production activation requires all of the following evidence:

- live Supabase schema reconciled with the canonical schema contract;
- migration history reconciled;
- RLS policies reviewed and approved;
- transaction/RPC implementation tested against the live schema;
- round-trip persistence tests pass;
- duplicate/retry tests pass;
- stale-version concurrency tests pass;
- rollback/partial-failure tests pass;
- restart/recovery tests pass;
- privacy and retention controls verified;
- legacy JSONL ownership and migration plan verified;
- provider activation is explicit and reversible.

Until this gate is satisfied, `InMemoryCivicCaseRepository` remains the active development adapter and the Supabase provider remains a verified-but-not-production-enabled implementation.
