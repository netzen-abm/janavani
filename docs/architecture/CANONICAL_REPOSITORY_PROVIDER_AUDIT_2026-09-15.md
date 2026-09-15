# Janavani — Canonical Repository / Provider Audit

**Date:** 15 September 2026  
**Baseline:** `main` after PR #165 merge  
**Main merge commit:** `aff94ae52dfaf13cd45d9a9b9aa4e36e7d298b7b`  
**Scope:** canonical storage contracts, provider adapters, transaction boundaries, and production-persistence readiness  
**Status:** AUDIT / NO PRODUCTION MIGRATION AUTHORIZED

## 1. Executive conclusion

Janavani has already crossed the important architectural boundary from generic application storage toward domain-specific repositories. The repository layer now contains provider-neutral contracts plus several PostgreSQL adapters, and the Civic Case path has a shared PostgreSQL Unit-of-Work boundary.

The next step should **not** be another generic storage abstraction and should **not** be an immediate database migration.

The highest-value remaining gap is **canonical provider composition and durable coverage for the capabilities that have become authoritative since the earlier PostgreSQL work**. In particular, the current provider-selection pattern is strongest for Civic Case and selected supporting domains, while newer canonical capabilities such as accountability feedback and external-channel verification do not yet have equivalent PostgreSQL repository/provider boundaries.

This means the architecture is ready for a controlled persistence-hardening phase, but not yet for declaring the entire Janavani ecosystem production-durable.

## 2. Verified repository/provider landscape

### Durable PostgreSQL adapters already present

The current tree contains PostgreSQL implementations for at least:

- Civic Case — `postgres_civic_case.py`
- Authority — `postgres_authority.py`
- Consent — `postgres_consent.py`
- Evidence metadata — `postgres_evidence.py`
- Document artifact metadata — `postgres_document_artifact.py`
- Policy — `postgres_policy.py`
- Submission — `postgres_submission.py`
- Case transaction — `postgres_case_transaction.py`
- Submission + Case transaction — `postgres_submission_case_transaction.py`

The PostgreSQL Civic Case implementation uses Psycopg 3 and the shared Unit-of-Work boundary. It supports injected connection factories as well as `JANAVANI_POSTGRES_DSN`, preserving deployment/provider freedom.

### Provider-selection boundaries

The repository already has explicit provider factories for several domains. The Civic Case provider selector supports `memory`, `postgres`, and `supabase`; development defaults to `memory`, while durable providers are selected explicitly.

This is a sound pattern because surfaces do not select concrete database implementations themselves.

### Development / migration adapters

The repository also contains in-memory implementations and compatibility adapters such as CSV/JSONL providers. These must remain development, reference, or migration boundaries unless and until their durability and operational guarantees are explicitly promoted.

## 3. Transaction boundary assessment

The provider-neutral `UnitOfWork` contract exists and the PostgreSQL implementation owns one connection and its transaction lifecycle.

The Civic Case PostgreSQL repository already persists the case projection, lifecycle events, evidence references, and document references through a shared transaction boundary.

This is the correct architectural direction.

However, the Unit-of-Work should remain a **storage transaction primitive**, not become a cross-provider distributed transaction abstraction. External government delivery must remain outside the database transaction, with explicit UNKNOWN/FAILED outcomes and independent acknowledgement evidence.

## 4. Important remaining gaps

### A. New canonical capabilities lack equivalent durable repository coverage

The recently established canonical boundaries for accountability feedback and external channel verification are authoritative at the capability level, but the current audit does not find PostgreSQL repository implementations for those domains.

This is acceptable for the current free/development phase, but it is a production-readiness gap.

Recommendation: implement durable adapters only when the corresponding capability actually requires persistence. Do not create speculative tables for capabilities that are still decision-only or development-only.

### B. Provider composition is not yet a single ecosystem-wide composition contract

Provider selection exists per domain. That is preferable to surfaces selecting databases, but production will eventually need one explicit composition/configuration boundary that constructs the complete canonical capability graph without allowing one surface to silently select a different persistence provider.

Recommendation: create a provider-neutral composition contract for the canonical persistence graph before production cutover. It should validate that all required durable capabilities are using compatible providers and transaction boundaries.

### C. Real target schema evidence is still the gate for migration

The existing PostgreSQL migration draft correctly remains review-only. The repository documentation explicitly states that production SQL execution is not authorized until the real PostgreSQL/Supabase schema, migration history, constraints, indexes, RLS policies, functions/triggers, and identity mapping are inspected.

No migration should be executed merely because the repository contains a conceptual schema.

### D. Free-service development should remain memory-first

For the current development phase, the default `memory` provider is appropriate. It avoids silently creating an external dependency and allows the product to be developed without paying for database infrastructure.

When durable persistence becomes necessary, PostgreSQL should be enabled through the existing provider-neutral boundary rather than introducing a new storage layer.

## 5. What should NOT be done now

- Do not create another generic `StorageService` or `StorageAdapter`.
- Do not delete legacy JSONL/CSV sources.
- Do not automatically migrate empty legacy JSONL sources.
- Do not make Supabase-specific APIs part of domain contracts.
- Do not introduce an ORM merely to simplify CRUD.
- Do not make external transport part of a database transaction.
- Do not force every capability to receive PostgreSQL persistence before it has a real persistence requirement.
- Do not make a single access surface the owner of storage.

## 6. Recommended implementation order

1. Establish and document the **canonical persistence composition contract**.
2. Add contract-level provider conformance tests so each durable adapter is tested against the same repository semantics.
3. Add PostgreSQL adapters for the newest canonical persisted domains only where product behavior requires durable state.
4. Verify the real target PostgreSQL schema and RLS/migration history.
5. Perform controlled production migration only after the evidence gates in the existing PostgreSQL migration contract are satisfied.
6. Keep legacy sources read-only until migration validation and rollback evidence are complete.

## 7. Decision

**Approved:** continue persistence-hardening through provider-neutral composition and bounded domain-specific adapters.  
**Not approved:** production migration, deletion of legacy sources, or vendor-specific domain coupling.

The next bounded implementation should therefore be the **canonical provider composition / persistence readiness boundary**, not a new generic storage abstraction.
