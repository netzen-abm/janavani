# Janavani — Canonical Civic Case Database Contract

**Status:** CANONICAL DESIGN CONTRACT — implementation pending
**Scope:** Civic Case durable persistence
**Principle:** PostgreSQL/Supabase is the authoritative relational store; application workflow remains in the domain/service layer.

## 1. Purpose

This contract maps the channel-neutral `CivicCase` domain object to durable relational storage without making the domain model depend on Supabase, PostgreSQL, Telegram, Web, mobile, DApp, or any other transport.

This document is a schema contract, not a claim that the schema or durable provider is already deployed.

## 2. Canonical ownership

```text
CivicCase domain
      |
      v
CivicCaseRepository
      |
      v
PostgreSQL / Supabase
      |
      +-- case records
      +-- case events
      +-- consent records
      +-- evidence/document references
      +-- submission/delivery records
      +-- audit metadata

Binary artifacts -> object storage
Ephemeral state  -> Redis/cache
RAG index        -> derived store
Transport        -> adapter
```

No transport may become the source of truth for a case.

## 3. Tables

### 3.1 `civic_cases`

One row is the durable aggregate record for one `CivicCase`.

| Column | Type | Required | Notes |
|---|---|---:|---|
| `case_id` | text/UUID | yes | Stable opaque identifier; primary key. |
| `case_type` | text | yes | Maps to `CaseType`. |
| `subject` | text | yes | Current citizen-editable subject. |
| `narrative` | text | yes | Current citizen-editable narrative. |
| `created_by` | text/UUID | no | User/entity reference; nullable for anonymous/pseudonymous flows. |
| `related_office_id` | text/UUID | no | Canonical government-office reference. |
| `status` | text | yes | Maps to `CaseStatus`. |
| `created_at` | timestamptz | yes | Creation timestamp. |
| `updated_at` | timestamptz | yes | Last aggregate update. |
| `version` | bigint | yes | Optimistic-concurrency version. |

`status` is a projection of the domain aggregate. Workflow transitions remain domain logic and must not be encoded as database business logic.

### 3.2 `civic_case_events`

Append-oriented lifecycle history. The event history is required to preserve corrections, approvals, evidence additions, submission state and acknowledgement history.

| Column | Type | Required | Notes |
|---|---|---:|---|
| `event_id` | text/UUID | yes | Primary key; globally unique. |
| `case_id` | text/UUID | yes | Foreign key to `civic_cases`. |
| `event_type` | text | yes | Maps to `CaseEventType`. |
| `occurred_at` | timestamptz | yes | Event time in UTC. |
| `actor_id` | text/UUID | no | Acting user/service identity. |
| `source_channel` | text | no | Adapter/channel that originated the event. |
| `source_ref` | text/UUID | no | Optional external/source reference. |
| `notes` | text | no | Non-sensitive event note; sensitivity policy applies. |
| `metadata_json` | jsonb | no | Structured metadata only where contractually required. |
| `event_version` | integer | yes | Event schema version. |

Event IDs must be unique. Events must never be silently overwritten.

### 3.3 `civic_case_consents`

Explicit consent records are separate durable objects. A case must not infer consent from channel access or case creation.

| Column | Type | Required | Notes |
|---|---|---:|---|
| `consent_id` | text/UUID | yes | Primary key. |
| `case_id` | text/UUID | yes | Foreign key. |
| `purpose` | text | yes | Purpose of consent. |
| `scope` | jsonb | yes | Explicit scope. |
| `status` | text | yes | Granted/denied/revoked/expired. |
| `granted_by` | text/UUID | no | Actor/entity reference. |
| `created_at` | timestamptz | yes | UTC. |
| `expires_at` | timestamptz | no | Optional expiry. |
| `revoked_at` | timestamptz | no | Optional revocation time. |
| `proof_ref` | text | no | Reference to consent proof/artifact. |

### 3.4 `civic_case_evidence_refs`

The case stores references, not large binary evidence payloads.

| Column | Type | Required | Notes |
|---|---|---:|---|
| `case_id` | text/UUID | yes | Foreign key. |
| `evidence_id` | text/UUID | yes | Canonical evidence object reference. |
| `relationship` | text | yes | Supports/contradicts/attachment/source/other. |
| `created_at` | timestamptz | yes | UTC. |

Primary key should be the `(case_id, evidence_id, relationship)` tuple unless the canonical evidence model requires a separate reference ID.

Binary evidence belongs in object storage; PostgreSQL stores metadata, provenance, hashes and access-policy references.

### 3.5 `civic_case_document_refs`

| Column | Type | Required | Notes |
|---|---|---:|---|
| `case_id` | text/UUID | yes | Foreign key. |
| `document_id` | text/UUID | yes | Canonical document reference. |
| `relationship` | text | yes | Draft/output/attachment/submission-document etc. |
| `created_at` | timestamptz | yes | UTC. |

PDF/DOCX binaries belong in object storage or the canonical document artifact store, not in the case row.

### 3.6 `civic_case_submissions`

Submission is separate from case status because local preparation, transport attempt, external delivery and acknowledgement are different facts.

| Column | Type | Required | Notes |
|---|---|---:|---|
| `submission_id` | text/UUID | yes | Primary key. |
| `case_id` | text/UUID | yes | Foreign key. |
| `destination_ref` | text/UUID | yes | Versioned authority/destination reference. |
| `document_ref` | text/UUID | no | Document submitted/exported. |
| `channel` | text | yes | Transport adapter identifier. |
| `state` | text | yes | Created/queued/transmitting/submitted/received/acknowledged/failed as supported. |
| `attempted_at` | timestamptz | no | Attempt timestamp. |
| `submitted_at` | timestamptz | no | Submission event timestamp. |
| `acknowledged_at` | timestamptz | no | Only when actual acknowledgement evidence exists. |
| `external_reference` | text | no | Destination acknowledgement/reference number. |
| `ack_ref` | text | no | Evidence/reference for acknowledgement. |
| `error_code` | text | no | Structured failure code. |
| `retry_count` | integer | yes | Defaults to zero. |

**Critical rule:** `SUBMITTING`, `QUEUED`, `SUBMITTED`, or local persistence must never be represented as government acknowledgement.

### 3.7 `civic_case_audit`

Security/accountability audit records may reference the case without duplicating private case content.

| Column | Type | Required | Notes |
|---|---|---:|---|
| `audit_id` | text/UUID | yes | Primary key. |
| `case_id` | text/UUID | yes | Foreign key. |
| `actor_id` | text/UUID | no | Acting identity. |
| `action` | text | yes | Audited action. |
| `occurred_at` | timestamptz | yes | UTC. |
| `result` | text | yes | Success/failure/partial. |
| `reason` | text | no | Safe reason code/message. |
| `source_channel` | text | no | Originating adapter. |
| `metadata_hash` | text | no | Integrity/provenance digest where appropriate. |

## 4. Relationships

```text
civic_cases
   |
   +----< civic_case_events
   |
   +----< civic_case_consents
   |
   +----< civic_case_evidence_refs >---- evidence
   |
   +----< civic_case_document_refs >---- documents
   |
   +----< civic_case_submissions
   |
   +----< civic_case_audit
```

Foreign keys must prevent orphaned case references unless an explicit archival/deletion policy requires tombstones.

## 5. Domain-to-storage mapping

| Domain field | Durable representation |
|---|---|
| `case_id` | `civic_cases.case_id` |
| `case_type` | `civic_cases.case_type` |
| `subject` | `civic_cases.subject` |
| `narrative` | `civic_cases.narrative` |
| `created_by` | `civic_cases.created_by` |
| `related_office_id` | `civic_cases.related_office_id` |
| `evidence_refs` | `civic_case_evidence_refs` |
| `document_refs` | `civic_case_document_refs` |
| `consent_refs` | `civic_case_consents` |
| `status` | `civic_cases.status` projection |
| `events` | `civic_case_events` ordered by `occurred_at` plus deterministic tie-breaker |

Hydration must reconstruct a valid `CivicCase` aggregate without changing domain semantics.

## 6. Concurrency and idempotency

The repository must support optimistic concurrency using `version` or an equivalent compare-and-swap mechanism.

Repeated writes with the same `event_id` must be idempotent or rejected deterministically. A retry must not duplicate a lifecycle event.

Submission retries must be represented as separate attempts or explicit retry state, not by overwriting the historical attempt.

## 7. Privacy and authorization

The production provider must implement least-privilege access and Row Level Security where Supabase is used.

Minimum rules:

- A citizen can access only cases they are authorized to access.
- Anonymous/pseudonymous cases must not expose identity metadata through ordinary case APIs.
- Sensitive case classes require stronger access policies than ordinary complaints.
- Evidence binaries are protected independently from case metadata.
- Consent scope must be evaluated before optional disclosure or cross-channel linking.
- Audit records must avoid unnecessary replication of sensitive narrative content.
- Retention, legal hold, archival and deletion/anonymisation policies must be explicit.

## 8. Authority and destination integrity

`related_office_id` and submission `destination_ref` must point to versioned canonical authority data where available.

A user correction is a candidate correction, not an automatic canonical overwrite. Destination corrections require source/provenance, verification and history.

## 9. Transaction boundaries

The durable provider must treat the aggregate update and its corresponding lifecycle event as one atomic operation where practical.

For submission workflows, case state, submission attempt and audit event must have a defined consistency model. External delivery cannot be made atomic with PostgreSQL; therefore external acknowledgement remains an independently evidenced fact.

## 10. Indexing requirements

At minimum:

- primary key on `civic_cases.case_id`;
- index on `(created_by, updated_at)`;
- index on `(status, updated_at)`;
- index on `civic_case_events(case_id, occurred_at)`;
- unique index on `civic_case_events.event_id`;
- index on `civic_case_submissions(case_id, attempted_at)`;
- index on destination reference;
- indexes supporting authorized user access and retention operations.

Exact indexes must be validated against actual query patterns before production rollout.

## 11. Migration rule

Do not perform a big-bang migration.

```text
Current legacy path
      |
      v
Inventory / preservation
      |
      v
Canonical schema mapping
      |
      v
Migration + validation
      |
      v
Controlled cutover
      |
      v
Legacy read-only / archive
```

No legacy CSV/JSONL store is approved for deletion by this contract.

## 12. Production verification gate

The durable provider is not production-ready until all are demonstrated:

1. Schema migration succeeds on a clean database.
2. `CivicCase` save/get round-trip preserves all contract fields.
3. Event ordering and idempotency are verified.
4. Concurrent updates cannot silently overwrite changes.
5. Unauthorized reads/writes are rejected by application and database policy.
6. RLS policies are tested with representative roles.
7. Restart does not lose committed cases/events.
8. Database outage produces deterministic degraded behavior.
9. External submission failure does not falsely create acknowledgement.
10. Backup/restore procedure is tested.
11. Sensitive case isolation is tested.
12. Retention/archive behavior is tested.
13. No email-sending behavior is introduced by case persistence; generated civic documents remain print/download artifacts unless a separately approved capability contract changes this rule.

## 13. Explicit non-goals

This contract does **not**:

- put workflow logic into PostgreSQL;
- require blockchain/Web3/Nostr/mesh availability;
- make Telegram or Web the canonical owner;
- store binary evidence directly in ordinary case rows;
- claim that Supabase is already production-configured;
- authorize automatic government acknowledgement;
- approve deletion of legacy data.

## 14. Status

**Schema contract:** DEFINED

**Database migration:** NOT IMPLEMENTED

**Durable repository:** NOT IMPLEMENTED

**RLS/security verification:** NOT IMPLEMENTED

**Production activation:** NOT APPROVED
