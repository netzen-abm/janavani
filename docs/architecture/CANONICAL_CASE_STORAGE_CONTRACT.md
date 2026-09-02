# Canonical Case Storage Contract

**Status:** Implemented boundary; durable provider pending verification.

## Purpose

The Civic Case lifecycle in `src/core/civic_case.py` is the canonical domain contract. Persistence belongs behind `src/storage/` and must not be owned by Web, Telegram, mobile, DApp, or other interface adapters.

## Contract

```text
CivicCase
    ↓
CivicCaseRepository
    ├── in-memory provider (tests/development)
    └── durable provider (production, pending verification)
```

The repository contract exposes only:

- `save(case)`
- `get(case_id)`

The domain object remains independent of Supabase and other storage providers.

## Current implementation

`InMemoryCivicCaseRepository` is used by the current HTTP adapter. This preserves the existing contract-verification behavior while removing direct dictionary ownership from the route handlers.

It is **not production persistence**. Process restart still loses state.

## Durable target

The existing repository audit identifies Supabase/PostgreSQL as the intended durable relational authority, with object storage for binary artifacts and Redis reserved for ephemeral state.

A durable Civic Case provider must be verified against the existing schema, access-control model, serialization/hydration requirements, audit events, and privacy rules before the HTTP adapter is switched to it.

## Evidence boundary

Case storage may persist evidence metadata and references, but the case repository must not silently upload citizen evidence bytes. Evidence content remains governed by the Evidence capability and its local-first/privacy boundary.

## Migration rule

Do not migrate or delete legacy JSONL/CSV stores as part of this contract change. Existing storage audits classify those stores as migration sources and require schema mapping, validation, reference removal, tests, production verification, rollback capability, and archive preservation before retirement.

## Next durable-provider gate

Before production activation:

1. Verify the current Supabase schema against the canonical `CivicCase` lifecycle.
2. Implement serialization/hydration with round-trip tests.
3. Implement authorization/RLS behavior and negative-access tests.
4. Persist lifecycle events without equating persistence with delivery acknowledgement.
5. Verify restart durability and failure recovery.
6. Only then replace the development provider in the canonical runtime.
