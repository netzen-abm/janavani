# Canonical Civic Case PostgreSQL Schema Contract

**Status:** Design contract — implementation pending verification
**Scope:** Durable persistence for the channel-neutral `CivicCase` and its lifecycle events.
**Authority:** `src/core/civic_case.py` + `docs/DATA_CONTRACTS.md`

## 1. Purpose

Define the relational shape required before a production Civic Case repository is connected to PostgreSQL/Supabase. This document is a mapping and verification contract, not a migration. No table, column, policy, or legacy store is changed by this document.

The canonical flow is:

```text
CivicCase
    -> CivicCaseRepository
        -> Durable PostgreSQL adapter
            -> PostgreSQL / Supabase
```

Interface adapters (Web, Telegram, mobile, DApp, WhatsApp, etc.) must not write database records directly.

## 2. Canonical aggregate

The durable aggregate is composed of:

```text
civic_cases
  ├── civic_case_events
  ├── civic_case_claims          (when claims become first-class persisted objects)
  ├── civic_case_evidence_refs
  ├── civic_case_document_refs
  ├── civic_case_consents
  └── civic_case_submissions     (delivery capability boundary)
```

Binary evidence and generated document files are **not** stored in the case row. PostgreSQL stores metadata/references; object storage owns binary artifacts.

## 3. `civic_cases`

| Column | Type | Null | Rule |
|---|---|---:|---|
| `case_id` | UUID/text opaque ID | NO | Primary key; stable and non-semantic |
| `case_type` | text/enum | NO | Must map exactly to canonical `CaseType` |
| `subject` | text | NO | Non-empty after trim |
| `narrative` | text | NO | Non-empty after trim |
| `created_by` | UUID/text | YES | Identity reference; anonymous/pseudonymous cases must remain supported where policy permits |
| `jurisdiction` | jsonb | NO | Structured jurisdiction object; versioned by application contract |
| `related_organisation_id` | UUID/text | YES | FK/reference to canonical organisation record |
| `related_office_id` | UUID/text | YES | FK/reference to canonical office record |
| `related_official_id` | UUID/text | YES | FK/reference to canonical official record |
| `related_representative_id` | UUID/text | YES | FK/reference to representative record |
| `claims` | jsonb | NO | User claims remain distinguishable from verified findings; normalize later if query requirements justify it |
| `consent_refs` | jsonb/relationship | NO | References to explicit consent records; must not be treated as a boolean shortcut |
| `status` | text/enum | NO | Canonical `CaseStatus`; transition controlled by domain/service layer |
| `created_at` | timestamptz | NO | UTC |
| `updated_at` | timestamptz | NO | UTC; updated on aggregate mutation |
| `version` | bigint | NO | Optimistic-concurrency version; starts at 1 and increments atomically |

### Constraints

- Primary key on `case_id`.
- `case_type` and `status` must reject values outside the canonical contract.
- `created_at <= updated_at`.
- `version >= 1`.
- A case cannot become `READY` without an explicit valid consent reference.
- Database constraints must not silently invent lifecycle transitions; transition authority remains in the domain/service layer.

## 4. `civic_case_events`

Lifecycle history is append-oriented and must survive case-row updates.

| Column | Type | Null | Rule |
|---|---|---:|---|
| `event_id` | UUID/text opaque ID | NO | Primary key; idempotency key |
| `case_id` | UUID/text | NO | FK/reference to `civic_cases` |
| `event_type` | text/enum | NO | Canonical `CaseEventType` |
| `occurred_at` | timestamptz | NO | UTC event time |
| `actor_id` | UUID/text | YES | Actor/identity reference |
| `source_channel` | text | YES | Adapter/source identifier; never business logic |
| `source_ref` | text | YES | External acknowledgement/delivery/source reference where applicable |
| `notes` | text | YES | Human-readable event context; sensitive data must be minimized |
| `event_version` | integer | NO | Contract/schema version |
| `created_at` | timestamptz | NO | Persistence timestamp |
| `metadata_hash` | text | YES | Optional integrity/audit hash |

### Constraints and indexes

- Primary key: `event_id`.
- Index: `(case_id, occurred_at)`.
- Unique idempotency key: `event_id`.
- Event `case_id` must match an existing case.
- Event history must not be deleted as part of ordinary case edits.
- A persisted acknowledgement must include a meaningful `source_ref` whenever an external acknowledgement reference exists.
- Persistence of a `SUBMITTED` event is never evidence of government acknowledgement.

## 5. Evidence references

`civic_case_evidence_refs` should contain relationships, not evidence bytes:

| Column | Type | Rule |
|---|---|---|
| `case_id` | UUID/text | FK to case |
| `evidence_id` | UUID/text | Reference to Evidence capability object |
| `relationship` | text | Purpose/context of evidence relationship |
| `created_at` | timestamptz | UTC |
| `created_by` | UUID/text | Actor reference |

Primary/unique key: `(case_id, evidence_id, relationship)`.

Evidence metadata must preserve provenance, SHA-256 where applicable, storage reference, access policy, retention policy, and transformation history according to the canonical Evidence contract. The case repository must not upload evidence bytes implicitly.

## 6. Document references

`civic_case_document_refs` should link cases to the canonical Document capability:

| Column | Type | Rule |
|---|---|---|
| `case_id` | UUID/text | FK to case |
| `document_id` | UUID/text | Reference to generated/attached document |
| `relationship` | text | e.g. draft, final, enclosure |
| `version` | integer | Document relationship version |
| `created_at` | timestamptz | UTC |

The document binary belongs in object storage. The case record stores the stable reference and lifecycle relationship.

Generated civic documents are for citizen review and print/download. The case persistence layer must not introduce an email-sending side effect.

## 7. Consent

Consent is a separate capability/record, not merely a case flag.

Minimum persisted fields must map to the canonical `Consent` contract:

```text
consent_id
subject_id
purpose
scope
 grant_type
status
created_at
expires_at
revoked_at
proof_ref
```

A case can reference consent records. Revoked/expired consent must not silently remain valid for a later submission operation.

## 8. Submission / delivery boundary

A separate `civic_case_submissions` table is required for delivery state because case lifecycle and transport delivery are related but not identical.

Minimum fields:

| Column | Type | Rule |
|---|---|---|
| `submission_id` | UUID/text | Primary key |
| `case_id` | UUID/text | FK to case |
| `destination_ref` | UUID/text/jsonb | Verified destination metadata reference |
| `transport` | text | Web/manual/Telegram/etc. adapter identifier |
| `status` | text | Queue/transmission/submission/delivery state from canonical delivery contract |
| `external_reference` | text | External submission/ack reference, nullable |
| `submitted_at` | timestamptz | UTC, nullable |
| `acknowledged_at` | timestamptz | UTC, nullable |
| `failure_reason` | text | Nullable; operational failure only |
| `created_at` | timestamptz | UTC |
| `updated_at` | timestamptz | UTC |
| `version` | bigint | Optimistic concurrency |

**Critical rule:** `SUBMITTING`, `QUEUED`, `SUBMITTED`, or local persistence must not be presented as government acknowledgement. `ACKNOWLEDGED` requires evidence/reference from the destination or an explicitly verified acknowledgement mechanism.

## 9. Audit boundary

Case mutations should emit canonical `AuditEvent` records through the audit capability. The case event stream is lifecycle history; audit events answer who/what/result/reason questions. They must not be collapsed into one overloaded table without explicit contract approval.

Minimum audit fields:

```text
event_id
actor_id
action
object_type
object_id
occurred_at
result
reason
source_channel
metadata_hash
```

## 10. Serialization / hydration contract

A durable repository must provide lossless round-trip behavior:

```text
CivicCase
  -> serialize
  -> PostgreSQL
  -> hydrate
  -> CivicCase
```

Round-trip equality must cover:

- case identity/type/status
- subject and narrative
- creator
- jurisdiction
- all authority references
- claims
- evidence references
- document references
- consent references
- event IDs/types/timestamps/actors/channels/source refs/notes

Unknown future fields must not be silently converted into incorrect values. Contract versioning is required for incompatible schema evolution.

## 11. Concurrency and idempotency

The repository must protect against lost updates and duplicate external operations.

Required behavior:

1. Use optimistic concurrency (`version`) or an equivalent atomic compare-and-swap mechanism.
2. Reject stale writes rather than silently overwriting a newer case.
3. Treat `event_id` as an idempotency key for event persistence.
4. Submission operations require a separate idempotency key/reference so retries cannot create duplicate submissions.
5. Domain transition validation occurs before persistence.
6. Database transactions must atomically persist the case version change and its lifecycle event where both are part of one domain operation.

## 12. Index strategy

Initial indexes should support:

- `civic_cases(created_by, updated_at)`
- `civic_cases(status, updated_at)`
- `civic_cases(related_office_id, status)`
- `civic_cases(related_organisation_id, status)`
- `civic_case_events(case_id, occurred_at)`
- `civic_case_submissions(case_id, status)`

Additional indexes require measured query need. Avoid indexing sensitive free-text fields by default.

## 13. Retention and privacy

- Apply retention policy per data class, not one global case TTL.
- Archive superseded records where lawful and useful.
- Legal holds override ordinary deletion schedules where applicable.
- Sensitive case categories require stronger access controls and may require separate storage/policy boundaries.
- Deletion/anonymization must preserve only what is legally/operationally required.
- Do not expose private case content through public search, analytics, logs, or ordinary error messages.

## 14. RLS dependency

PostgreSQL/Supabase Row Level Security is a security control, not a substitute for domain authorization.

Before implementation, define the authorization matrix for:

- case creator
- explicitly authorized delegate
- case support/operator role
- destination/government role where applicable
- administrator
- system service
- public/anonymous caller

No RLS SQL is authorized by this document.

## 15. Verification gate

The durable provider is **not production-ready** until all are demonstrated:

1. Existing schema/migrations are inspected.
2. Schema mapping above is reconciled with actual deployed schema.
3. RLS/authorization matrix is approved.
4. Serialization/hydration round-trip tests pass.
5. Lifecycle event persistence tests pass.
6. Duplicate/retry/idempotency tests pass.
7. Concurrent update tests pass.
8. Restart durability is demonstrated.
9. Failure/rollback behavior is demonstrated.
10. Privacy/retention behavior is verified.
11. Legacy JSONL/CSV migration is separately planned and validated.
12. Only then is the in-memory provider replaced in production runtime.

## 16. Explicit non-goals

This contract does not:

- create or alter PostgreSQL tables;
- create or alter RLS policies;
- migrate legacy CSV/JSONL;
- delete/archive existing files;
- upload evidence or documents;
- send email;
- make AI mandatory;
- make blockchain/Web3/Nostr/mesh/satellite a dependency;
- authorize production deployment.
