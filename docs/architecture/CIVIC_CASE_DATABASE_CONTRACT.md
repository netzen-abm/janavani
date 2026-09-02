# Janavani — Canonical Civic Case Database Contract

**Status:** CANONICAL DESIGN CONTRACT — implementation pending  
**Scope:** Civic Case durable persistence  
**Principle:** PostgreSQL/Supabase is the authoritative relational store; application workflow remains in the domain/service layer.

## 1. Purpose

This contract maps the channel-neutral Civic Case capability to durable relational storage without making the domain model depend on Supabase, PostgreSQL, Telegram, Web, mobile, DApp, or any other transport.

This is a schema contract, not a claim that the schema or durable provider is deployed.

## 2. Reconciliation rules

The existing canonical data contract defines a Case with jurisdiction, organisation/office/official/representative references, claims, evidence, documents and consent. The database model must preserve those fields rather than silently dropping them.

The current runtime `CivicCase` implementation is a narrower aggregate. The durable provider must therefore either hydrate only fields actually represented by the runtime aggregate or, before provider activation, extend the runtime aggregate to the canonical Case contract. No persistence implementation may discard canonical fields merely because the current Python model has not yet exposed them.

The canonical data contract also defines additional case types (`CORRUPTION`, `MISBEHAVIOUR`, `TRANSFER_CONCERN`) that must be reconciled with the runtime `CaseType` enum before production activation.

## 3. Canonical ownership

```text
Civic Case capability
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
      +-- authority references
      +-- evidence/document references
      +-- submission/delivery records
      +-- audit metadata

Binary artifacts -> object storage
Ephemeral state  -> Redis/cache
RAG index        -> derived store
Transport        -> adapter
```

No transport may become the source of truth for a case.

## 4. Tables

### 4.1 `civic_cases`

One row is the durable aggregate record for one case.

| Column | Type | Required | Notes |
|---|---|---:|---|
| `case_id` | text/UUID | yes | Stable opaque identifier; primary key. |
| `case_type` | text | yes | Must support the canonical Case type set. |
| `subject` | text | yes | Current citizen-editable subject. |
| `narrative` | text | yes | Current citizen-editable narrative. |
| `created_by` | text/UUID | no | User/entity reference; nullable for anonymous/pseudonymous flows. |
| `jurisdiction_json` | jsonb | yes | Canonical jurisdiction value; exact normalized shape must be defined before migration. |
| `related_organisation_id` | text/UUID | no | Canonical government-organisation reference. |
| `related_office_id` | text/UUID | no | Canonical government-office reference. |
| `related_official_id` | text/UUID | no | Canonical government-official reference. |
| `related_representative_id` | text/UUID | no | Canonical elected-representative reference. |
| `subject_claims_json` | jsonb | yes | Canonical `Claim[]`; must distinguish citizen claims from verified facts. |
| `status` | text | yes | Durable projection of lifecycle status. |
| `created_at` | timestamptz | yes | UTC creation timestamp. |
| `updated_at` | timestamptz | yes | UTC last aggregate update. |
| `version` | bigint | yes | Optimistic-concurrency version. |

`status` is a projection of domain state. Workflow transitions remain domain/service logic and must not be encoded as database business logic.

### 4.2 `civic_case_events`

Append-oriented lifecycle history. It preserves corrections, approvals, evidence additions, submission state, acknowledgement and subsequent follow-up.

| Column | Type | Required | Notes |
|---|---|---:|---|
| `event_id` | text/UUID | yes | Primary key; globally unique. |
| `case_id` | text/UUID | yes | Foreign key to `civic_cases`. |
| `event_type` | text | yes | Must cover the canonical event set plus any implementation-only lifecycle events. |
| `occurred_at` | timestamptz | yes | UTC event time. |
| `actor_id` | text/UUID | no | Acting user/service identity. |
| `source_channel` | text | no | Adapter/channel that originated the event. |
| `source_ref` | text | no | External/source reference. |
| `notes` | text | no | Non-sensitive event note; sensitivity policy applies. |
| `metadata_json` | jsonb | no | Structured metadata only where contractually required. |
| `event_version` | integer | yes | Event schema version. |

Events must never be silently overwritten.

### 4.3 `civic_case_consents`

Explicit consent records are separate durable objects. Case creation or channel access never implies consent.

| Column | Type | Required | Notes |
|---|---|---:|---|
| `consent_id` | text/UUID | yes | Primary key. |
| `case_id` | text/UUID | yes | Foreign key. |
| `purpose` | text | yes | Purpose of consent. |
| `scope` | jsonb | yes | Explicit scope. |
| `grant_type` | text | no | Canonical consent grant mechanism. |
| `status` | text | yes | Granted/denied/revoked/expired. |
| `granted_by` | text/UUID | no | Actor/entity reference. |
| `created_at` | timestamptz | yes | UTC. |
| `expires_at` | timestamptz | no | Optional expiry. |
| `revoked_at` | timestamptz | no | Optional revocation time. |
| `proof_ref` | text | no | Reference to consent proof/artifact. |

### 4.4 `civic_case_evidence_refs`

The case stores references, not large binary evidence payloads.

| Column | Type | Required | Notes |
|---|---|---:|---|
| `case_id` | text/UUID | yes | Foreign key. |
| `evidence_id` | text/UUID | yes | Canonical evidence object reference. |
| `relationship` | text | yes | Relationship of evidence to case. |
| `created_at` | timestamptz | yes | UTC. |

Binary evidence belongs in object storage. PostgreSQL stores metadata, provenance, hashes and access-policy references.

### 4.5 `civic_case_document_refs`

| Column | Type | Required | Notes |
|---|---|---:|---|
| `case_id` | text/UUID | yes | Foreign key. |
| `document_id` | text/UUID | yes | Canonical document reference. |
| `relationship` | text | yes | Draft/output/attachment/submission-document/etc. |
| `created_at` | timestamptz | yes | UTC. |

PDF/DOCX binaries belong in the canonical document artifact store/object storage, not ordinary case rows.

### 4.6 `civic_case_submissions`

Submission is separate from case status because preparation, transport attempt, external receipt and acknowledgement are different facts.

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

**Critical rule:** `SUBMITTING`, `QUEUED`, `SUBMITTED`, local persistence or transport success must never be represented as government acknowledgement.

### 4.7 `civic_case_audit`

Security/accountability audit records reference cases without unnecessarily duplicating private case content.

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

## 5. Authority integrity

`related_organisation_id`, `related_office_id`, `related_official_id`, `related_representative_id` and submission `destination_ref` must reference canonical, versioned authority data where available.

A user correction is a candidate change, not an automatic canonical overwrite. Corrections require source/provenance, verification and history as defined by the canonical authority-data contract.

## 6. Domain-to-storage mapping

| Canonical Case field | Durable representation |
|---|---|
| `case_id` | `civic_cases.case_id` |
| `case_type` | `civic_cases.case_type` |
| `created_by` | `civic_cases.created_by` |
| `subject` | `civic_cases.subject` |
| `narrative` | `civic_cases.narrative` |
| `jurisdiction` | `civic_cases.jurisdiction_json` |
| `related_organisation_id` | `civic_cases.related_organisation_id` |
| `related_office_id` | `civic_cases.related_office_id` |
| `related_official_id` | `civic_cases.related_official_id` |
| `related_representative_id` | `civic_cases.related_representative_id` |
| `claims` | `civic_cases.subject_claims_json` |
| `evidence_refs` | `civic_case_evidence_refs` |
| `document_refs` | `civic_case_document_refs` |
| `consent_refs` | `civic_case_consents` |
| `status` | `civic_cases.status` projection |
| lifecycle history | `civic_case_events` |

Hydration must not silently discard canonical fields. Where the runtime aggregate is temporarily narrower than the canonical contract, provider activation must be blocked until the mismatch is resolved.

## 7. Concurrency and idempotency

The repository must support optimistic concurrency using `version` or an equivalent compare-and-swap mechanism.

Repeated writes with the same `event_id` must be idempotent or rejected deterministically. Retries must not duplicate lifecycle events.

Submission retries must preserve attempt history rather than overwriting the prior attempt.

## 8. Privacy and authorization

The production provider must implement least-privilege access and Row Level Security where Supabase is used.

Minimum requirements:

- citizens access only cases they are authorized to access;
- anonymous/pseudonymous cases do not expose identity metadata through ordinary case APIs;
- sensitive case classes receive stronger access policies where required;
- evidence binaries are protected independently from case metadata;
- consent scope is evaluated before optional disclosure or cross-channel linking;
- audit records avoid unnecessary narrative replication;
- retention, legal hold, archival and deletion/anonymisation policies are explicit.

## 9. Transaction boundaries

The durable provider should persist the aggregate update and corresponding lifecycle event atomically where practical.

For submission workflows, case state, submission attempt and audit event require a defined consistency model. External delivery cannot be made atomic with PostgreSQL; acknowledgement therefore remains an independently evidenced fact.

## 10. Indexing requirements

At minimum:

- primary key on `civic_cases.case_id`;
- indexes supporting authorized user access;
- index on `(status, updated_at)`;
- index on `civic_case_events(case_id, occurred_at)`;
- unique index on `civic_case_events.event_id`;
- index on `civic_case_submissions(case_id, attempted_at)`;
- index on destination references;
- indexes supporting retention/archive operations.

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
2. Case save/get round-trip preserves all canonical fields represented by the runtime model.
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
13. No email-sending behavior is introduced by case persistence; generated civic documents remain print/download artifacts unless a separately approved capability contract changes that rule.
14. Runtime `CaseType` and `CaseStatus` enums are demonstrably aligned with the canonical data contract before production activation.

## 13. Explicit non-goals

This contract does not:

- put workflow logic into PostgreSQL;
- require blockchain/Web3/Nostr/mesh availability;
- make Telegram or Web the canonical owner;
- store binary evidence directly in ordinary case rows;
- claim that Supabase is already production-configured;
- authorize automatic government acknowledgement;
- approve deletion of legacy data.

## 14. Status

**Database contract:** DEFINED and RECONCILED against the currently inspected canonical Case data contract.  
**Database migration:** NOT IMPLEMENTED.  
**Durable repository:** NOT IMPLEMENTED.  
**RLS/security verification:** NOT IMPLEMENTED.  
**Production activation:** NOT APPROVED.
