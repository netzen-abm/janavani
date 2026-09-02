# Janavani — PostgreSQL Implementation Specification

**Status:** IMPLEMENTATION SPECIFICATION — migration not yet authorized
**Scope:** Durable Civic Case persistence
**Source contracts:** `src/core/civic_case.py`, `docs/DATA_CONTRACTS.md`, `docs/architecture/CANONICAL_CASE_POSTGRES_SCHEMA.md`, `docs/architecture/CIVIC_CASE_DATABASE_CONTRACT.md`, `docs/architecture/CANONICAL_CASE_RLS_AUTHORIZATION_MATRIX.md`

## 1. Purpose

This specification converts the verified Civic Case contracts into an implementation sequence for PostgreSQL/Supabase. It is intentionally non-destructive: it does not authorize production schema changes, RLS activation, legacy-data deletion, or production deployment.

## 2. Canonical tables

The first durable case slice requires these relational boundaries:

1. `civic_cases`
2. `civic_case_events`
3. `civic_case_consents`
4. `civic_case_evidence_refs`
5. `civic_case_document_refs`
6. `civic_case_submissions`
7. `civic_case_audit`

Binary evidence and generated document artifacts remain outside ordinary case rows in object storage. PostgreSQL stores references and metadata.

## 3. `civic_cases`

Required columns:

```text
case_id                       opaque text/UUID primary key
case_type                     text/enum, canonical CaseType
subject                       text, non-empty
narrative                     text, non-empty
created_by                    opaque identity reference, nullable
jurisdiction_json             jsonb, required
related_organisation_id       nullable authority reference
related_office_id             nullable authority reference
related_official_id           nullable authority reference
related_representative_id     nullable authority reference
subject_claims_json           jsonb, required
status                        text/enum, canonical CaseStatus
created_at                    timestamptz, UTC
updated_at                    timestamptz, UTC
version                       bigint, starts at 1
```

Implementation rules:

- `case_type` must include every runtime `CaseType` value.
- `status` must include every runtime `CaseStatus` value.
- `created_by` must support anonymous/pseudonymous cases where the selected policy permits them.
- `version` is the optimistic-concurrency boundary.
- Database constraints may enforce structural validity but must not become the source of lifecycle workflow logic.

## 4. `civic_case_events`

Required columns:

```text
event_id                     opaque primary key / idempotency key
case_id                      foreign key to civic_cases
event_type                   canonical CaseEventType
occurred_at                  timestamptz, UTC
actor_id                     nullable identity reference
source_channel               nullable adapter identifier
source_ref                   nullable external/source reference
notes                        nullable, minimized
metadata_json                nullable structured metadata
event_version               integer
created_at                   timestamptz, UTC
```

Required indexes:

- primary key on `event_id`;
- `(case_id, occurred_at)`;
- optional query-specific indexes only after measurement.

Events are append-oriented. Ordinary case edits must never overwrite historical lifecycle events.

## 5. Consent boundary

`civic_case_consents` must represent explicit, purpose-bound consent independently of authentication.

Required conceptual fields:

```text
consent_id
case_id
purpose
scope
status
grant_type
granted_by
created_at
expires_at
revoked_at
proof_ref
```

Submission authorization must evaluate current consent state. A historical consent reference alone must not bypass expiry or revocation.

## 6. Evidence boundary

`civic_case_evidence_refs` stores relationships only:

```text
case_id
evidence_id
relationship
created_at
created_by
```

Evidence bytes remain in the evidence/object-storage capability. Case persistence must not implicitly upload binary evidence.

## 7. Document boundary

`civic_case_document_refs` stores relationships only:

```text
case_id
document_id
relationship
version
created_at
```

Generated civic documents remain reviewable, printable and downloadable artifacts. Persistence must not add email-sending side effects.

## 8. Submission boundary

`civic_case_submissions` separates case lifecycle from external delivery facts.

Required conceptual fields:

```text
submission_id
case_id
destination_ref
document_ref
channel
state
attempted_at
submitted_at
acknowledged_at
external_reference
ack_ref
error_code
retry_count
version
created_at
updated_at
```

`SUBMITTING`, `QUEUED`, `SUBMITTED`, local persistence, or transport success cannot manufacture government acknowledgement. An acknowledgement requires independently evidenced destination information.

## 9. Audit boundary

`civic_case_audit` records security/accountability events without unnecessarily copying private narratives.

Required conceptual fields:

```text
audit_id
case_id
actor_id
action
occurred_at
result
reason
source_channel
metadata_hash
```

Lifecycle events and security audit events remain distinct concepts.

## 10. Repository contract

The durable provider must implement the existing provider-neutral `CivicCaseRepository` boundary. The domain model must remain independent of Supabase/PostgreSQL.

Minimum required behavior:

```text
save(case) -> persisted case
get(case_id) -> case or not-found
```

The production implementation must also provide, directly or through a compatible repository extension:

- lossless serialization/hydration;
- optimistic concurrency;
- deterministic duplicate-event handling;
- atomic case-version/event persistence where one domain operation changes both;
- deterministic database failure behavior.

## 11. Serialization contract

Every currently represented runtime field must round-trip without loss:

```text
case_id
case_type
subject
narrative
created_by
jurisdiction
related_organisation_id
related_office_id
related_official_id
related_representative_id
claims
evidence_refs
document_refs
consent_refs
status
events
```

Every event must preserve:

```text
event_id
case_id
event_type
occurred_at
actor_id
source_channel
source_ref
notes
```

Unknown future fields must not be silently mapped to incorrect values.

## 12. Concurrency and idempotency

The provider must:

1. require the caller's expected version for mutation where concurrency applies;
2. atomically reject stale versions;
3. treat `event_id` as an idempotency key;
4. prevent duplicate lifecycle events from retrying the same operation;
5. use a separate submission idempotency boundary for external delivery attempts;
6. preserve attempt history rather than overwriting previous submission attempts.

## 13. Transaction boundaries

For ordinary domain mutations:

```text
authorize
  -> validate transition
  -> persist aggregate projection + event atomically
```

For external submission:

```text
authorize
  -> validate consent
  -> persist/prepare submission attempt
  -> external transport
  -> persist external result
  -> persist acknowledgement only when evidenced
```

PostgreSQL cannot make an external government transmission atomic. The data model must therefore preserve uncertainty and failure rather than invent success.

## 14. Identity mapping prerequisites

The database implementation must use the canonical identity boundary. It must not create a second citizen identity model.

Authentication and identity are separate from authorization, and authorization is separate from consent. The database identity mapping must therefore be documented before RLS activation.

## 15. RLS prerequisites

RLS implementation is a later gated step. Before activation, define database-visible mappings for at least:

- anonymous caller;
- citizen/principal owner;
- explicitly authorized delegate;
- support/operator;
- destination service;
- government actor where applicable;
- administrator;
- system service;
- auditor.

Application authorization and RLS are complementary controls. RLS must not replace domain lifecycle validation.

## 16. Required negative tests

The implementation test suite must demonstrate at minimum:

1. Citizen A cannot read Citizen B's private case.
2. Citizen A cannot edit Citizen B's case.
3. Inactive delegate is denied.
4. Revoked delegate is denied.
5. Anonymous caller cannot enumerate private cases.
6. Citizen cannot fabricate an acknowledgement.
7. Historical lifecycle events cannot be modified through ordinary case editing.
8. A case evidence reference does not grant unrestricted binary access.
9. Destination service cannot read unrelated cases.
10. Administrative access is auditable.
11. Expired/revoked consent cannot authorize submission.
12. Persisting a submission cannot manufacture acknowledgement.
13. Cross-user/cross-tenant queries cannot bypass ownership controls.
14. Stale-version writes are rejected.

## 17. Migration sequence

No big-bang migration.

```text
Legacy CSV/JSONL
      ↓
Inventory + preservation
      ↓
Canonical mapping
      ↓
Clean PostgreSQL schema
      ↓
Migration validation
      ↓
Repository integration
      ↓
Controlled cutover
      ↓
Legacy read-only
      ↓
Archive after evidence
```

No deletion is part of this specification.

## 18. Verification gate

The durable provider remains non-production until all of the following are demonstrated:

- clean-database migration;
- save/get round-trip;
- complete event persistence;
- idempotency;
- concurrency protection;
- restart durability;
- database outage behavior;
- backup/restore;
- application authorization;
- RLS negative tests;
- sensitive-case isolation;
- retention/archive behavior;
- authority provenance/correction behavior;
- document print/download-only invariant;
- runtime/canonical enum alignment.

## 19. Current decision

**APPROVED FOR SPECIFICATION ONLY.**

The next implementation may create a migration in a controlled reviewable change, but production activation and RLS remain separately gated. No legacy data may be deleted or silently migrated without validation evidence.
