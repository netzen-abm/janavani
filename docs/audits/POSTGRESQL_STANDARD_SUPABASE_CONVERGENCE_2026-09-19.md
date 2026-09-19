# Janavani — PostgreSQL Standard / Supabase Runtime-Build Convergence Audit
Date: 2026-09-19
Status: ACTIVE CONVERGENCE — runtime/build removal substantially implemented; execution evidence pending

## Decision

Janavani owns the capability. PostgreSQL is the relational standard. Supabase is not required by the Janavani runtime, build, CI, configuration or startup architecture.

Historical Supabase implementation material is preserved under archive/legacy/ and must not re-enter the active dependency graph.

## 1. Prior-audit alignment

This audit deliberately does not repeat the earlier repository, runtime-entrypoint, storage-ownership, capability-mapping, or architecture audits. It consumes those results and checks only the unresolved delta:

1. active Supabase dependency graph;
2. PostgreSQL provider selection;
3. active build/configuration references;
4. conformance/security gate readiness;
5. master-task reprioritization.

Earlier evidence established that the direct PostgreSQL CivicCase provider is the stronger current durable implementation, uses the shared Unit-of-Work boundary, and already has disposable PostgreSQL integration coverage for round-trip, concurrency and rollback. The historical Supabase provider did not claim multi-table atomicity.

## 2. Changes completed in this pass

- Removed the active Supabase CivicCase implementation path.
- Removed the active Supabase smoke test.
- Preserved historical Supabase implementation/test material under archive/legacy/.
- Removed the Supabase Python dependency from requirements.txt.
- Removed the Supabase Python dependency from pyproject.toml.
- Removed Supabase runtime variables from src/core/config.py.
- Removed Supabase variables from .env.example.
- Reduced CivicCase provider selection to memory/postgres.
- Removed Supabase repository exports from the active repository package.
- Added tests/test_postgres_provider_conformance.py to guard the active build/runtime surface against reintroduction of Supabase imports, package dependencies and environment variables.
- Rebased active architecture documents so PostgreSQL is the relational standard and historical Supabase references are no longer treated as an active provider.

## 3. Active dependency sweep result

### Imports
The canonical provider factory now imports only the PostgreSQL adapter for the durable path. No active provider selection path accepts a Supabase client.

### Build dependencies
requirements.txt and pyproject.toml no longer declare the Supabase package.

### Configuration
The active environment contract uses JANAVANI_POSTGRES_DSN and PostgreSQL provider selection. Supabase credentials are no longer part of the active .env.example or core configuration.

### CI
The canonical CI workflow installs requirements.txt plus the PostgreSQL extra and starts PostgreSQL 16 for integration tests. No Supabase dependency is declared by the workflow.

### Startup/deployment
The prior runtime-entrypoint audit already established canonical FastAPI startup. This pass does not change startup ownership; it removes the database-provider dependency from the active graph.

### Documentation
Active architecture/governance references were converged to PostgreSQL. Dated historical audits and archive material may still mention Supabase because they are evidence of the previous architecture and must remain traceable.

## 4. PostgreSQL conformance/security gate

### Existing evidence
The repository already contains:
- atomic Case + event/reference transaction boundaries;
- rollback integration coverage;
- optimistic concurrency rejection;
- Submission + Case atomic orchestration;
- exact replay/idempotency coverage;
- canonical RLS authorization matrix;
- explicit negative-test requirements.

### Gate still required for production readiness
1. Execute real PostgreSQL atomic Case writes.
2. Execute forced rollback and prove zero partial state.
3. Execute stale-writer/concurrency tests.
4. Execute exact replay and conflicting idempotency tests.
5. Execute application authorization negative tests.
6. Execute PostgreSQL RLS negative tests.
7. Execute cross-user/cross-case isolation tests.
8. Execute restart durability.
9. Execute outage/degraded-mode behavior.
10. Execute backup/restore evidence.
11. Record exact CI/runtime evidence for the current main commit.

## 5. Important non-completion

Removing Supabase does not mean PostgreSQL is production-ready.

The current production gate remains blocked until authorization, RLS, restart/recovery, outage behavior, backup/restore, consent persistence and complete submission consistency are verified.

## 6. Master execution priority

P0 — finish active dependency/build/startup/documentation convergence.
P0 — run the PostgreSQL conformance/security gate.
P1 — close consent persistence and authorization/RLS gaps.
P1 — finish capability -> repository -> test -> deployment mapping.
P1 — complete runtime/deployment evidence for canonical Web/API and independent Telegram.
P2 — consolidate/archive verified legacy generations.
P2 — resume broader ecosystem capabilities only after the canonical foundation passes its gates.

## Exit condition

Do not declare this work complete because files were edited.

The exit condition is:
active Supabase dependency scan = clean;
PostgreSQL conformance/security gate = green with evidence;
production migration/RLS = separately approved;
master checklist = synchronized with exact evidence.
