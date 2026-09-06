# Janavani — Durable Provider Readiness Audit

**Status:** AUDIT COMPLETE — production activation remains blocked
**Scope:** PostgreSQL and Supabase CivicCase providers
**Date:** 2026-09-06

## Executive decision

The canonical PostgreSQL schema and provider boundaries are sufficiently defined for continued implementation, but neither durable provider is approved for production activation.

The direct PostgreSQL provider has a stronger transaction boundary than the Supabase adapter. The Supabase adapter explicitly does not claim multi-table atomicity. Both providers still require production evidence for authorization, RLS, restart durability, backup/restore, outage behavior, and full submission consistency.

## Verified strengths

- Canonical `CivicCase` fields are represented in the Rust and Python domain models.
- Heterogeneous JSON values are represented through the canonical Rust JSON object type.
- Serialization/schema conformance is enforced automatically.
- A shared cross-language JSON fixture now exercises Python and Rust round-trip compatibility.
- PostgreSQL persistence uses injected connection construction and an explicit unit-of-work boundary.
- Optimistic concurrency is represented through the case `version` field.
- Event identifiers are treated as idempotency keys by the persistence implementation.
- Binary evidence is represented as references rather than ordinary case-row payloads.
- Generated documents remain separate artifacts.

## Blocking findings

### 1. Production schema is still a draft

`POSTGRESQL_MIGRATION_DRAFT.sql` is explicitly review-only. It excludes RLS and production configuration and requires clean-database testing before execution.

### 2. Supabase provider lacks verified multi-table atomicity

The Supabase adapter performs case, event and reference writes through separate API operations. Its own implementation documentation states that multi-table atomicity is not claimed. It must not replace the PostgreSQL provider as a production write path until a verified transaction/RPC boundary exists.

### 3. PostgreSQL provider needs live integration evidence

The current repository tests use a fake connection/database. They establish provider mechanics and concurrency behavior but do not prove behavior against a real PostgreSQL instance.

Required next evidence includes clean schema creation, save/get round-trip, rollback behavior, duplicate-event behavior, stale-version rejection and restart durability against an actual disposable PostgreSQL database.

### 4. Authorization and RLS are not activated

The database contract requires application authorization plus database-level policy verification where Supabase is used. Role mappings and negative tests remain a production gate.

### 5. Submission consistency is incomplete

Case persistence is not the same as external submission. Submission attempt, external result and acknowledgement require their own consistency model and idempotency boundary. No database write may manufacture acknowledgement.

### 6. Canonical contract reconciliation remains a gate

The database contract requires runtime/canonical enum alignment before production activation. The implementation must continue to treat this as an explicit verification gate rather than infer approval from schema compatibility alone.

## Required automated gates

The following should remain deterministic CI checks where practical:

- Python/Rust field parity;
- JSON serialization fixture round-trip;
- lifecycle matrix parity;
- provider-boundary scanning;
- surface separation;
- archive safety evidence;
- migration schema linting;
- migration-to-model field coverage;
- line-length ratchet;
- secret/dependency checks;
- repository test suite.

Automation must detect and report. It must not silently activate providers, execute production migrations, enable RLS, delete legacy data, or retire surfaces.

## Required production evidence before activation

1. Disposable clean PostgreSQL migration succeeds.
2. Real PostgreSQL save/get preserves every runtime field.
3. Real PostgreSQL event persistence is complete and ordered.
4. Duplicate event IDs are deterministic under retry.
5. Stale versions cannot overwrite newer state.
6. Rollback leaves no partial aggregate/event/reference state.
7. Restart preserves committed state.
8. Database outage produces deterministic degraded behavior.
9. Backup/restore is demonstrated.
10. Application authorization negative tests pass.
11. Supabase RLS negative tests pass if Supabase is activated.
12. Sensitive-case isolation is demonstrated.
13. Submission retry history is preserved.
14. External failure cannot create acknowledgement.
15. Consent expiry/revocation blocks unauthorized submission.
16. Authority provenance and correction rules are demonstrated.
17. Retention/archive behavior is tested.
18. No persistence path introduces document email side effects.

## Decision

**Continue with controlled provider verification. Do not activate durable production persistence yet.**

The next implementation slice should establish real PostgreSQL integration tests on a disposable database and validate the draft schema against the canonical provider contract. RLS and production activation remain separate gated decisions.
