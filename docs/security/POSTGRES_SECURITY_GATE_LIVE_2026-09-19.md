# PostgreSQL Security Gate — Live Janavani Reconciliation (2026-09-19)

**Status:** BLOCKED pending identity/RLS contract reconciliation  
**Project:** Janavani Supabase project `sysiblufgixbqqsdbywn`  
**Purpose:** Record verified live-database evidence before any RLS activation.

## Verified live state

The connected Janavani database is PostgreSQL 17.6.1.155 in ap-south-1.

The canonical Civic Case tables exist in `public`, including:

- `civic_cases`
- `civic_case_events`
- `civic_case_evidence_refs`
- `civic_case_document_refs`
- `civic_case_consents`
- `civic_case_submissions`
- `janavani_delegation_grants`
- `janavani_service_identity_policies`

All eight currently have **RLS disabled**.

This is a **critical security finding**. With the Supabase Data API role model, these tables must not remain exposed without a deliberately approved authorization boundary.

**Do not enable RLS by itself.** Enabling RLS without policies would block ordinary access, while enabling incomplete policies could create false security.

## Schema reconciliation findings

The live schema does not exactly match the repository migration draft.

Examples:

- live `civic_cases.jurisdiction` vs draft `jurisdiction_json`
- live `civic_cases.claims` vs draft `subject_claims_json`
- live `civic_cases.consent_refs` exists in the live database
- live submission columns use `transport`, `status`, and `failure_reason`, while the draft migration uses a different naming model
- live `civic_case_document_refs` has a composite primary key including `version`
- live `civic_case_consents` has no `case_id`, `granted_by`, or `proof_ref` columns
- live migration history contains the canonical case-policy and submission-idempotency migrations

Therefore the repository SQL must not be treated as a byte-for-byte description of the currently deployed database.

## Authorization prerequisites

Before production RLS:

1. Canonical Janavani identity mapping must be durable and verified.
2. Authentication/session identity must be mapped to the canonical principal.
3. Database-visible principal context must be defined.
4. Case ownership must map to `civic_cases.created_by`.
5. Delegation lookup and revocation semantics must be verified.
6. Service identities must be separated by capability where practical.
7. Consent must be reconciled with the live consent schema.
8. Sensitive-case classification must be defined.
9. Negative-access tests must be executable against the actual database.
10. Rollback must be tested.

## Required negative tests

At minimum:

1. Citizen A cannot read Citizen B's case.
2. Citizen A cannot update Citizen B's case.
3. Anonymous caller cannot enumerate private cases.
4. Revoked delegate cannot access the case.
5. Expired delegate cannot access the case.
6. Destination service cannot read unrelated cases.
7. Client cannot directly rewrite lifecycle history.
8. Case authorization does not grant evidence-byte access.
9. Consent revocation blocks a new submission operation.
10. Submission persistence cannot manufacture acknowledgement.

## Current decision

**RLS activation is not yet authorized by the existing repository contracts.**

The next implementation unit is the identity/database authorization mapping and live-schema reconciliation. Only after that should a candidate RLS migration be authored and negative-tested.

## Supabase platform note

Supabase currently recommends RLS for tables in exposed schemas and separates table grants from row-level policy. New public tables are also moving toward explicit Data API grants rather than automatic exposure. The Janavani design therefore needs both layers deliberately defined.

