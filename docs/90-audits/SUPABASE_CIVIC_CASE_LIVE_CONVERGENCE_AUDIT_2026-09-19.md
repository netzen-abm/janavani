# Supabase Civic Case Live Convergence Audit — 2026-09-19

**Status:** EVIDENCE / CRITICAL SECURITY GAP IDENTIFIED
**Project:** Janavani (`sysiblufgixbqqsdbywn`)
**Region:** `ap-south-1`
**Database:** PostgreSQL 17.6
**Scope:** Live schema, migrations, RLS/security, transaction readiness, repository alignment

## 1. Executive finding

The live Janavani Supabase project is healthy and contains the expected Civic Case relational tables, but it is **not production-safe for citizen case data in its current access-control state**.

### Critical finding

RLS is disabled and there are zero policies on all eight sensitive public tables:

- `civic_cases`
- `civic_case_events`
- `civic_case_evidence_refs`
- `civic_case_document_refs`
- `civic_case_consents`
- `civic_case_submissions`
- `janavani_delegation_grants`
- `janavani_service_identity_policies`

The live Supabase security advisor independently reports this as a critical RLS finding.

**Do not expose these tables to untrusted browser/client access in this state.**

## 2. Live database evidence

The project is active/healthy.

The database contains the expected Civic Case tables and foreign-key relationships.

Current row counts checked directly:

- `civic_cases`: 0
- `civic_case_events`: 0
- `civic_case_submissions`: 0

This means the database can be brought into a controlled security state without requiring a live-data migration for existing case records.

## 3. Migration evidence

The live project reports two migrations:

- `20260912100000` — `canonical_case_policy_schema`
- `20260913100000` — `submission_idempotency_key`

Migration names are not treated as proof of semantic completeness; the deployed schema remains the source for runtime reconciliation.

## 4. Schema alignment findings

The deployed schema uses `jurisdiction`, `claims`, and `consent_refs` on `civic_cases`, while parts of the repository provider contract use `jurisdiction_json` and `subject_claims_json` and a relational consent representation.

The deployed `civic_case_submissions` table also differs in naming/shape from parts of the canonical document: it uses `destination_ref` as `jsonb`, plus `transport`, `status`, `idempotency_key`, and version fields.

These differences must be reconciled before provider activation. One canonical provider contract must own the mapping.

## 5. Repository/provider finding

The direct PostgreSQL provider uses a transaction/unit-of-work boundary and optimistic concurrency.

The current Supabase repository performs case write, event persistence, and reference persistence as separate client operations, and its source explicitly does not claim multi-table atomicity.

Therefore:

> **SupabaseCivicCaseRepository is not transactionally equivalent to PostgresCivicCaseRepository.**

A partial failure could leave a case projection committed while an event/reference write fails.

## 6. Identity/RLS finding

The live tables use identifiers such as `created_by`, while the Janavani identity contract requires a Janavani-owned opaque identity boundary.

RLS must therefore be based on the verified Janavani identity/authentication model, not Telegram IDs, phone numbers, email addresses, or arbitrary adapter identifiers.

## 7. Recommended target architecture

```text
Citizen / Surface
      |
      v
Janavani IdentityContext
      |
      v
Authorization / Policy
      |
      v
Civic Case Capability
      |
      v
Repository Contract
      |
      +--------------------+
      |                    |
      v                    v
PostgreSQL Provider    Supabase Adapter
      |                    |
      +--------+-----------+
               |
        Canonical schema
               |
         RLS / policy layer
```

Supabase remains a provider, not the Janavani architecture.

## 8. RLS remediation — NOT applied

The live advisor-generated RLS enablement statements are recorded here for controlled review:

```sql
ALTER TABLE public.civic_cases ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.civic_case_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.civic_case_evidence_refs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.civic_case_document_refs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.civic_case_consents ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.civic_case_submissions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.janavani_delegation_grants ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.janavani_service_identity_policies ENABLE ROW LEVEL SECURITY;
```

**This was intentionally not executed.**

Enabling RLS without correct policies can block legitimate access, while guessed policies could introduce an authorization defect.

## 9. Performance evidence

The performance advisor reports eight unused indexes.

Because the Civic Case tables currently contain zero rows and are not yet under production traffic, these findings are not sufficient evidence that the indexes should be removed.

First define actual authorization predicates and workload; then optimize.

## 10. Transaction recommendation

Do not retrofit atomicity into the current Supabase repository by chaining more client calls and treating them as one logical transaction.

Preferred target:

```text
CivicCase capability
      |
      v
Provider-neutral mutation contract
      |
      +--------------------+
      |                    |
PostgreSQL UoW          Supabase RPC
      |                    |
      +---------+----------+
                |
          one logical commit
```

The Supabase RPC should be designed only after the live schema and RLS authorization matrix are reconciled.

## 11. Current production readiness

| Area | Evidence |
|---|---|
| Database active/healthy | YES |
| Civic Case schema exists | YES |
| Current Civic Case rows | 0 |
| Migration history | YES |
| RLS on sensitive case tables | NO |
| RLS policies | NONE |
| Direct PostgreSQL transaction path | Implemented, rollout gated |
| Supabase multi-table atomicity | Not verified / current adapter non-atomic |
| Production activation | NOT APPROVED |

## 12. Immediate engineering priorities

1. Define and approve the identity-to-case ownership matrix.
2. Define RLS policies from that matrix.
3. Reconcile deployed schema names/types with the canonical repository contract.
4. Design a single transactional Supabase RPC for case mutation.
5. Test the RPC on a non-production database.
6. Add shared repository conformance tests for PostgreSQL and Supabase.
7. Only then enable production RLS and consider durable activation.

## 13. Important non-actions

Do not:

- expose the current case tables directly to clients;
- enable RLS with guessed policies;
- delete or replace the PostgreSQL provider;
- call the Supabase adapter production-ready;
- remove unused indexes solely from the advisor report;
- make Supabase-specific APIs part of the Civic Case domain contract.