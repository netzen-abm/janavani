# Janavani — PostgreSQL Civic Case Migration Draft

**Status:** REVIEW-ONLY / NOT FOR EXECUTION  
**Scope:** Canonical Civic Case durable persistence  
**Authority:** `src/core/civic_case.py`, `docs/DATA_CONTRACTS.md`, `docs/architecture/CANONICAL_CASE_POSTGRES_SCHEMA.md`, `docs/architecture/POSTGRESQL_IMPLEMENTATION_SPEC.md`, `docs/architecture/CANONICAL_CASE_TRANSACTION_CONTRACT.md`  
**Production mutation:** NOT AUTHORIZED

## 1. Purpose

This document is the reconciled migration design for the first durable Civic Case PostgreSQL slice.

It is deliberately a **review draft**, not an executable migration. The repository currently does not contain a verified `supabase/migrations` directory or an inspected deployed PostgreSQL schema. Therefore no SQL in this document may be applied to production or treated as proof that the target database has these tables.

The design preserves the existing architecture:

```text
Interface adapter
      ↓
Civic Case capability
      ↓
CivicCaseRepository
      ↓
PostgreSQL / Supabase
```

Adapters do not write database records directly.

## 2. Reconciliation result

The current contracts converge on these first-class persistence boundaries:

1. `civic_cases`
2. `civic_case_events`
3. `civic_case_consents`
4. `civic_case_evidence_refs`
5. `civic_case_document_refs`
6. `civic_case_submissions`
7. `civic_case_audit`

The runtime aggregate currently represents `claims` as a list, so the first implementation should use `subject_claims_json` rather than prematurely introducing a separate claims table. A separate `civic_case_claims` table remains a future optimization if measured query requirements justify first-class claim objects.

The runtime `CivicCase` already contains `created_at`, `updated_at`, and `version`; those fields therefore remain part of the canonical case row. fileciteturn893file0L1-L2

The existing durable provider already maps these fields using `jurisdiction_json` and `subject_claims_json`, so the draft follows that established mapping rather than introducing a second naming convention.

## 3. Proposed schema shape

### 3.1 `civic_cases`

Conceptual definition:

```sql
CREATE TABLE civic_cases (
    case_id TEXT PRIMARY KEY,
    case_type TEXT NOT NULL,
    subject TEXT NOT NULL,
    narrative TEXT NOT NULL,
    created_by TEXT NULL,
    jurisdiction_json JSONB NOT NULL,
    related_organisation_id TEXT NULL,
    related_office_id TEXT NULL,
    related_official_id TEXT NULL,
    related_representative_id TEXT NULL,
    subject_claims_json JSONB NOT NULL DEFAULT '[]'::jsonb,
    status TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL,
    version BIGINT NOT NULL DEFAULT 1,
    CONSTRAINT civic_cases_version_positive CHECK (version >= 1),
    CONSTRAINT civic_cases_time_order CHECK (created_at <= updated_at)
);
```

**Important:** the `CREATE TABLE` block is illustrative only. Exact PostgreSQL types, enum/check strategy, foreign keys, defaults, and existing-column compatibility must be selected only after inspecting the real target schema.

Canonical runtime values must be reconciled from the source code before constraints are activated. The current runtime includes statuses such as `DRAFT`, `REVIEW`, `READY`, `SUBMITTING`, `QUEUED`, `SUBMITTED`, `ACKNOWLEDGED`, `FOLLOW_UP`, `IN_PROGRESS`, `RESPONDED`, `RESOLVED`, `ESCALATED`, `CLOSED`, and `ARCHIVED`. fileciteturn893file0L1-L2

### 3.2 `civic_case_events`

```sql
CREATE TABLE civic_case_events (
    event_id TEXT PRIMARY KEY,
    case_id TEXT NOT NULL,
    event_type TEXT NOT NULL,
    occurred_at TIMESTAMPTZ NOT NULL,
    actor_id TEXT NULL,
    source_channel TEXT NULL,
    source_ref TEXT NULL,
    notes TEXT NULL,
    metadata_json JSONB NULL,
    event_version INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMPTZ NOT NULL,
    metadata_hash TEXT NULL,
    FOREIGN KEY (case_id) REFERENCES civic_cases(case_id)
);
```

Required indexes:

```sql
CREATE INDEX civic_case_events_case_time_idx
    ON civic_case_events (case_id, occurred_at);
```

The primary key on `event_id` is also the first idempotency boundary. Lifecycle events remain append-oriented; ordinary case edits never overwrite historical events.

The current runtime event contract already includes `event_id`, `case_id`, `event_type`, `occurred_at`, `actor_id`, `source_channel`, `source_ref`, and `notes`. fileciteturn893file0L1-L2

### 3.3 Evidence references

```sql
CREATE TABLE civic_case_evidence_refs (
    case_id TEXT NOT NULL,
    evidence_id TEXT NOT NULL,
    relationship TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL,
    created_by TEXT NULL,
    PRIMARY KEY (case_id, evidence_id, relationship),
    FOREIGN KEY (case_id) REFERENCES civic_cases(case_id)
);
```

Evidence bytes are not part of the case row. The evidence/object-storage capability owns binary artifacts.

### 3.4 Document references

```sql
CREATE TABLE civic_case_document_refs (
    case_id TEXT NOT NULL,
    document_id TEXT NOT NULL,
    relationship TEXT NOT NULL,
    version INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMPTZ NOT NULL,
    PRIMARY KEY (case_id, document_id, relationship, version),
    FOREIGN KEY (case_id) REFERENCES civic_cases(case_id)
);
```

Generated documents remain reviewable, printable and downloadable. This persistence boundary introduces **no email-sending side effect**.

### 3.5 Consent

Consent remains an independently owned capability. The case repository may reference consent records but must not manufacture consent.

Conceptual fields:

```text
consent_id
case_id
purpose
scope
grant_type
status
granted_by
created_at
expires_at
revoked_at
proof_ref
```

Submission authorization must evaluate the current consent state. A historical reference is not a permanent authorization token.

### 3.6 Submission / delivery

```sql
CREATE TABLE civic_case_submissions (
    submission_id TEXT PRIMARY KEY,
    case_id TEXT NOT NULL,
    destination_ref JSONB NOT NULL,
    document_ref TEXT NULL,
    channel TEXT NOT NULL,
    state TEXT NOT NULL,
    attempted_at TIMESTAMPTZ NULL,
    submitted_at TIMESTAMPTZ NULL,
    acknowledged_at TIMESTAMPTZ NULL,
    external_reference TEXT NULL,
    ack_ref TEXT NULL,
    error_code TEXT NULL,
    retry_count INTEGER NOT NULL DEFAULT 0,
    version BIGINT NOT NULL DEFAULT 1,
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL,
    FOREIGN KEY (case_id) REFERENCES civic_cases(case_id),
    CONSTRAINT civic_case_submissions_version_positive CHECK (version >= 1),
    CONSTRAINT civic_case_submissions_retry_nonnegative CHECK (retry_count >= 0)
);
```

A separate submission idempotency key is required. Transport success or local persistence can never manufacture government acknowledgement.

### 3.7 Audit

```sql
CREATE TABLE civic_case_audit (
    audit_id TEXT PRIMARY KEY,
    case_id TEXT NULL,
    actor_id TEXT NULL,
    action TEXT NOT NULL,
    occurred_at TIMESTAMPTZ NOT NULL,
    result TEXT NOT NULL,
    reason TEXT NULL,
    source_channel TEXT NULL,
    metadata_hash TEXT NULL,
    FOREIGN KEY (case_id) REFERENCES civic_cases(case_id)
);
```

Lifecycle events and security/accountability audit records remain separate concepts.

## 4. Atomic mutation contract

The durable implementation must not reproduce the current multi-call development behavior in production. A lifecycle mutation that changes both the case projection and event history must commit as one database transaction.

Conceptual operation:

```text
persist_civic_case_mutation(
    case_id,
    expected_version,
    case_projection,
    lifecycle_event,
    idempotency_key
)
```

Transaction semantics:

```text
BEGIN
  verify case exists
  verify expected version
  verify event idempotency
  verify supplied transition was already authorized/validated
  update civic_cases and increment version
  insert civic_case_events
  persist same-operation refs when required
COMMIT
```

Any failure before commit must leave the case projection and its lifecycle event unchanged.

A stale `expected_version` must fail rather than overwrite a newer version.

A retry using the same event/idempotency key must produce deterministic behavior and must not duplicate the lifecycle event.

## 5. External submission is deliberately not one transaction

Government delivery occurs outside PostgreSQL's transaction boundary:

```text
authorize
  ↓
validate current consent
  ↓
persist submission attempt
  ↓
external transport
  ↓
persist transport result
  ↓
persist acknowledgement only when independently evidenced
```

The database must preserve an unknown or failed outcome rather than converting it to success.

## 6. Existing storage adapter boundary

`src/services/storage_adapter.py` currently provides a generic rating/complaint storage adapter with JSONL as its default and optional Supabase support. It writes to `ratings` and is not a substitute for the canonical `CivicCaseRepository`. fileciteturn890file0L2-L2

Therefore this work should **not** create another generic storage abstraction. The Civic Case repository remains the domain-specific durable boundary, while the older adapter should be separately assessed for eventual migration/deprecation after its consumers are inventoried.

## 7. Verification gate before any executable migration

Before converting this draft into an executable migration, verify all of the following against the real target:

- [ ] actual PostgreSQL/Supabase project identified;
- [ ] existing tables inspected;
- [ ] existing columns/types inspected;
- [ ] existing constraints inspected;
- [ ] existing indexes inspected;
- [ ] existing RLS policies inspected;
- [ ] existing functions/triggers inspected;
- [ ] Supabase migration history inspected;
- [ ] identity-to-database mapping approved;
- [ ] RLS authorization matrix approved;
- [ ] canonical enum values reconciled from runtime;
- [ ] clean-database migration test passes;
- [ ] save/get round-trip passes;
- [ ] lifecycle transaction atomicity passes;
- [ ] stale-version rejection passes;
- [ ] duplicate-event retry passes;
- [ ] restart durability passes;
- [ ] backup/restore passes;
- [ ] privacy/retention behavior passes;
- [ ] legacy CSV/JSONL migration is separately validated.

## 8. Legacy data rule

Current repository inventory shows legacy/local files such as `database/complaints.jsonl`, `database/offices.csv`, and `database/ratings.jsonl`. These remain preservation/migration sources until ownership is formally cut over.

No file is deleted by this draft.

The migration sequence remains:

```text
inventory
  → preserve
  → map
  → migrate
  → validate
  → controlled cutover
  → legacy read-only
  → archive after evidence
```

## 9. Decision

**Approved:** reconciled review design and transaction boundary.  
**Not approved:** production SQL execution, schema mutation, RLS activation, data migration, deletion, or deployment.

The next implementation step is to obtain/inspect the real PostgreSQL/Supabase schema and migration history. Only after that evidence is available should this review draft be converted into a controlled executable migration and transaction/RPC implementation.
