# JANAVANI — PRODUCTION PERSISTENCE GATE

**Date:** 27 August 2026  
**Branch:** `refactor/case-capability-kernel`  
**Status:** IN PROGRESS

## Decision

The Case/Evidence/Authority/Submission workflow now has an explicit durable-storage adapter boundary, but production persistence is **not yet claimed complete**.

The repository's storage ownership map identifies Supabase/PostgreSQL as the intended durable relational authority and calls for schema inspection, migrations, repositories/data-access, row-level security, backup/recovery and integration tests. fileciteturn650file0

## Implemented

- `src/storage/case_memory_repository.py` — development/test repository implementations.
- `src/storage/supabase_repositories.py` — explicit Supabase repository boundary.
- Case workflow API depends on repository interfaces rather than provider-specific business logic.
- Canonical FastAPI assembly mounts the workflow router.

## Not yet complete

- production canonical tables/migrations;
- serialization/deserialization mapping for Case, Evidence, Authority and Submission;
- transaction boundaries;
- row-level security policies;
- production service-role/user-role separation;
- integration tests against a controlled database environment;
- backup/restore verification;
- migration of legacy JSONL/CSV ownership;
- production deployment verification.

## Safety rule

Do not replace the development repository with a live Supabase implementation until the canonical schema and authorization model are verified. A configured Supabase client alone is not evidence that durable workflow persistence is production-ready.

## Next gate

1. inspect the actual database migrations/schema in the repository;
2. reconcile the canonical contracts with deployed table structure;
3. implement explicit repositories and transaction behavior;
4. add integration tests;
5. verify RLS and least privilege;
6. only then switch the runtime dependency from memory to durable storage.

**No production-complete claim is made by this document.**