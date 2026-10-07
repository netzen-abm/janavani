# PostgreSQL Provider Verification Gate — 2026-10-07

## Current decision

**Production activation remains blocked.**

The repository already contains a provider-neutral Unit-of-Work boundary and a PostgreSQL Case transaction implementation. Existing tests cover transaction lifecycle, optimistic concurrency/idempotency contracts, disposable PostgreSQL integration, and atomic consent+Case behavior.

This pass did not activate production persistence or RLS.

## Cross-check findings

### 1. Unit-of-Work boundary — PASS for architecture

`UnitOfWork` is provider-neutral and `PostgresUnitOfWork` owns connection/transaction lifecycle and transaction-local principal binding.


### 2. Case serialization — CORRECTED

Verification found a concrete mapping defect in the PostgreSQL Case codec: `case_type` had been supplied for the `subject` field and the narrative had been replaced with an empty string during both write and hydration. The provider boundary has been corrected to preserve the canonical `subject` and `narrative` fields, and a regression assertion now covers the round-trip.

### 3. Case + event atomicity — IMPLEMENTED, requires fresh real-DB evidence

`PostgresCaseTransactionRepository` locks the Case, checks idempotency, applies the projection mutation, appends the lifecycle event, and commits through one Unit of Work.

The canonical contract still requires real PostgreSQL evidence for rollback, retry, concurrency, restart and unknown-outcome behavior.

### 4. Consent + Case atomicity — IMPLEMENTED, schema reconciliation required

`PostgresConsentCaseAtomicRepository` writes consent metadata and the Case projection in one transaction.

The canonical migration already defines `civic_case_consents.case_id` and `granted_by`. The standalone `PostgresConsentRepository` schema initializer was missing those canonical columns; it has now been aligned structurally so the standalone provider does not create a conflicting table shape.

This change does **not** authorize production migration execution.

### 5. Evidence — provider boundary exists

Evidence metadata is separate from the Case aggregate and includes SHA-256/provenance/access/retention references. Production authorization/RLS coverage remains a gate.

### 6. Document artifact persistence — correctly isolated

Durable artifact persistence remains an explicit provider boundary. Primary WebApp/Telegram document download paths are ephemeral and do not require this durable path.

### 7. Schema authority — NOT YET PRODUCTION-VERIFIED

The repository contains both the canonical schema contract and a controlled migration. They still require reconciliation against the actual target PostgreSQL environment before production activation.

## Required evidence before production

1. Fresh disposable PostgreSQL migration.
2. Case + event commit/rollback tests on real PostgreSQL.
3. Consent + Case commit/rollback tests on real PostgreSQL.
4. Evidence persistence round-trip.
5. Document-reference round-trip.
6. RLS/authorization negative tests.
7. Restart durability.
8. Backup/restore.
9. Outage/unknown-transaction-outcome behavior.
10. Production migration review and approval.

## Non-goals of this pass

- No production database migration.
- No RLS activation.
- No provider activation.
- No legacy data migration.
- No new persistence abstraction.
- No branch creation.

## Branch invariant

The live repository remains exactly nine physical branches.
