# JANAVANI — DATABASE CANONICAL SCHEMA RECONCILIATION

**Date:** 27 August 2026  
**Branch:** `refactor/case-capability-kernel`  
**Status:** SCHEMA DRAFT COMMITTED / PRODUCTION DEPLOYMENT NOT VERIFIED

## 1. Finding

The repository's documented target database is Supabase/PostgreSQL. The planning design names `citizens`, `issues`, `evidence`, `locations`, `departments`, `offices`, `documents`, `submissions`, `conversations`, and `volunteers` as core tables. fileciteturn657file0

The repository does **not** currently expose an existing checked-in Supabase migration directory on the canonical ref inspected. The existing `src/storage/supabase.py` is only a conditional Supabase client initializer, not a durable repository implementation. fileciteturn652file0

Therefore no existing production schema can safely be assumed from repository evidence alone.

## 2. Canonical workflow schema introduced

An additive migration has been committed at:

`supabase/migrations/20260827_0001_canonical_case_workflow.sql`

It establishes the durable relational foundation for:

- `cases`
- `authorities`
- `evidence`
- `consents`
- `documents`
- `submissions`
- `case_events`
- `delivery_events`
- explicit case relationship tables

The schema deliberately keeps workflow/business logic in the application layer, consistent with the existing database design principle. fileciteturn657file0

## 3. Contract alignment

### Case

Maps the executable Case domain fields:

- ID
- issue
- status
- facts
- timestamps

The application Case additionally owns evidence/document/authority/submission/consent references and append-only domain events. fileciteturn702file0

### Evidence

Maps:

- evidence ID
- case ID
- kind
- title
- source
- status
- content reference
- capture timestamp
- metadata
- provenance

This matches the current executable evidence model, which deliberately keeps payload storage behind `content_ref` and requires provenance for verification. fileciteturn660file0

### Authority

Maps:

- authority ID
- name/type
- organisation/office references
- jurisdiction
- addresses/contact points/official URLs
- source references
- verification state
- verification timestamp

The executable model requires source references before an authority can be verified. fileciteturn661file0

### Consent

Maps the executable consent primitive including:

- subject
- capability
- purpose
- scope
- data categories
- grant type
- status
- policy version
- source channel
- grant/expiry/revocation/proof references

The current contract requires purpose-bound, auditable consent and separate approval for consequential external actions. fileciteturn688file0

### Submission

Maps:

- submission ID
- operation ID
- case
- destination
- status
- consent reference
- authorization reference
- payload hash
- timestamps

Delivery history is stored separately in `delivery_events`, matching the executable submission state machine. fileciteturn664file0

## 4. Important intentional differences from the older planning schema

The older planning document uses `issues` as the citizen problem object. fileciteturn657file0

The newer canonical application model uses `Case` as the durable civic-work unit and supports a broader lifecycle. This is an architectural evolution, not a claim that the old `issues` table exists or has been migrated.

Likewise, the older design lists `citizens`, while the current identity contract deliberately minimises identity and keeps authentication/linking as a separate access-control concern. fileciteturn701file0

## 5. Security posture

The migration enables row-level security on all new durable workflow tables but intentionally does not create permissive public policies.

This is a **safe default**, not a completed authorization model.

Before production use, the project still requires:

- authenticated user policy design;
- service-role separation;
- case ownership rules;
- sensitive-case isolation;
- consent-aware access rules;
- reviewer/admin permissions;
- audit/access logging;
- retention/legal-hold controls.

The master checklist currently identifies identity/access as an unstarted workstream and requires role/permission, revocation and access auditing. fileciteturn668file0

## 6. Legacy storage

No migration or deletion has been performed for:

- `database/complaints.jsonl`
- `database/ratings.jsonl`
- `database/offices.csv`

The storage ownership map classifies these as legacy/seed sources and requires runtime ownership verification before migration or archive. The JSONL complaint and rating stores are currently empty/near-empty in the inspected tree. fileciteturn656file0

The repository's existing complaint repository intentionally remains on JSONL until the canonical durable path is verified. fileciteturn713file0

## 7. Document gap discovered

`src/domain/document.py` is currently an empty placeholder. fileciteturn672file0

There is nevertheless a separate document-generation service with PDF and DOCX rendering functionality. fileciteturn692file0

Therefore the current state is:

```text
Document contract       DESIGN
Document domain model   PLACEHOLDER
Document generation     PARTIAL IMPLEMENTATION
Document persistence    SCHEMA PREPARED
```

A real canonical Document domain model should be implemented before claiming the full Case → Document → Submission workflow complete.

## 8. Production gate

The newly committed migration is **not** evidence that the database has been deployed.

Production persistence remains blocked until:

1. migration is applied to a controlled Supabase/PostgreSQL environment;
2. schema inspection succeeds;
3. repository serialization/deserialization is implemented;
4. transaction boundaries are defined;
5. RLS policies are reviewed and tested;
6. integration tests pass;
7. backup/restore is verified;
8. runtime deployment uses the intended database credentials/roles;
9. legacy ownership is migrated only after verification.

## 9. Status

**Schema draft:** IMPLEMENTED  
**Schema deployment:** NOT VERIFIED  
**Repository mapping:** BOUNDARY ONLY  
**RLS:** ENABLED / POLICIES NOT YET DEFINED  
**Legacy migration:** NOT STARTED  
**Production switch:** NOT AUTHORIZED

**Next engineering target:** implement the canonical `Document` domain model and then build executable serialization/repository tests against the new schema contract.
