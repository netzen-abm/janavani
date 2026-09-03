# Janavani Standard PostgreSQL Provider Contract

**Status:** IMPLEMENTED PROVIDER / PRODUCTION ROLLOUT STILL GATED

## Purpose

Janavani uses PostgreSQL as a portable relational standard without making any
single hosted PostgreSQL provider the platform architecture.

The canonical dependency direction is:

```text
Surface
  -> Adapter
  -> Capability Contract
  -> Domain
  -> Repository Contract
  -> PostgreSQL Provider
```

`PostgresCivicCaseRepository` is the standard direct-PostgreSQL provider.
Supabase remains a separate provider adapter. Neither provider is the domain
model or the capability contract.

## Provider requirements

The standard provider must:

- use PostgreSQL directly;
- avoid Supabase-specific APIs and types;
- keep the domain model provider-neutral;
- support injected connections for tests and deployment flexibility;
- use explicit transactions for multi-table Civic Case writes;
- enforce optimistic concurrency;
- preserve event and reference records;
- avoid storing binary evidence/document content in the case aggregate;
- fail without manufacturing submission or government acknowledgement;
- expose no provider-specific dependency to access surfaces.

## Driver

The implementation uses Psycopg 3 when a DSN is supplied. The dependency is
optional so Janavani can still run surfaces that do not use PostgreSQL.

Environment variable:

`JANAVANI_POSTGRES_DSN`

A deployment may instead inject a connection factory.

## Rollout gate

This implementation does **not** authorize a production database migration.
Before production use, Janavani must verify:

1. canonical schema against the actual target database;
2. versioned migration mechanism;
3. RLS/authorization matrix;
4. transaction and rollback behavior on a real PostgreSQL instance;
5. duplicate/retry/idempotency behavior;
6. concurrent updates;
7. restart and recovery;
8. privacy and retention controls;
9. legacy JSONL/CSV migration evidence;
10. provider contract tests against at least one disposable PostgreSQL deployment.

Only after those gates pass should a provider be selected as the runtime
backend for durable Civic Case data.
