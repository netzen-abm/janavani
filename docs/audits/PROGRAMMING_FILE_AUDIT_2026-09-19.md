# Janavani Programming File Audit — 2026-09-19

## Scope

Audited the default-branch repository tree for programming/build files, with emphasis on active runtime code rather than archived generations.

Repository snapshot: 95c4d5365bca0f2bc6350ce612f3aa70cec63e24.

Inventory:
- 748 total repository files
- 511 programming/build/config files
- 408 active programming/build/config files after excluding archive/janavani_v2/janavani_v3
- Active breakdown: 360 Python, 15 Rust, 5 SQL, 10 YAML, 2 TOML/YAML-family entries, 7 TOML, 8 shell, 1 JavaScript, plus workflow/config files.

## High-value findings

### P0 — Broken retired-provider export
`src/storage/repositories/__init__.py` still imported the retired `supabase_civic_case` module even though that module had already been removed from the active tree. This could break repository-package imports and contradicted the PostgreSQL-only active provider contract.

**Action:** removed the export. Historical provider remains archived.

### P0 — Empty active Supabase placeholder
`src/storage/supabase_client.py` was an empty active file. It created misleading active-tree evidence of a supported Supabase client despite the provider convergence decision.

**Action:** archived it at `archive/legacy/storage/supabase_client.py` and removed it from active source.

### P0 — Live RLS remains disabled
All eight inspected Civic Case/security tables have RLS disabled. No activation was performed during this audit.

### P0 — Real integration evidence is still conditional
The repository's real PostgreSQL integration tests are gated by `JANAVANI_POSTGRES_TEST_DSN`. Repository inspection alone cannot establish that those tests have actually passed on the current main commit.

### P1 — Canonical Case capability has application-level owner filtering
`CivicCaseCapability.get_owned()` filters by `created_by`. This is useful defense-in-depth, but it is not a substitute for database authorization/RLS and does not yet compose delegation at the capability query boundary.

### P1 — Submission repository creates schema at runtime
`PostgresSubmissionRepository._initialize()` contains `CREATE TABLE IF NOT EXISTS` and index creation. This duplicates migration ownership and should eventually be removed from runtime code so migrations own schema lifecycle.

### P1 — Runtime entrypoint split
`src/web/canonical_app.py` is the canonical FastAPI assembly, while `src/web/app.py` is a compatibility wrapper. `src/main.py` starts Telegram directly. This is architecturally intentional for surface independence, but deployment manifests must be verified so each deployment target points to its intended canonical entrypoint.

### P1 — Broad exception handling remains
Active code contains broad `except Exception` blocks in Telegram/conversation/submission/land/SOS/watchdog paths. Some are intentional transport-boundary fallbacks; others should be narrowed and structured logging should replace direct `print()` in production paths.

### P1 — Runtime test suite contains empty test modules
Several active test files are zero-byte placeholders (for example `test_documents.py`, `test_engine.py`, `test_registry.py`, `test_services.py`, `test_workflow.py`). They should either receive meaningful tests or be archived/removed after verifying that they are not required by CI.

### P1 — Multiple generations remain active
The repository still contains a large active Python surface plus Rust and Dioxus work. `janavani_v2` and `janavani_v3` are historical/parallel according to existing architecture records, but the active root also contains legacy-looking services/models. These should be resolved by import/runtime evidence rather than broad deletion.

### P2 — Rust direction is present but not yet the sole runtime
Rust core/application crates and Dioxus client code exist, while Python remains the dominant active runtime. The correct current strategy is convergence behind stable contracts, not a forced rewrite.

## Security-specific findings

- Identity assertion verification is cryptographically bounded by HMAC, issuer/audience checks, lifetime checks and opaque principal IDs.
- Authorization, consent, delegation and service-policy composition are separated.
- Candidate RLS policy uses transaction-local Janavani principal context rather than `auth.uid()`.
- Candidate RLS remains unactivated.
- Service-policy table is intended to be backend-controlled.
- Real cross-user/RLS execution evidence is still missing.

## Storage findings

Canonical direction:
- Civic Case: memory/postgres
- Submission: memory/postgres
- Durable artifact/evidence paths: PostgreSQL metadata plus external blob storage
- Supabase: historical evidence only

Remaining risk:
- runtime schema creation in PostgresSubmissionRepository
- provider-specific migration duplication
- some SQLite/local providers remain active for non-Case domains and need explicit lifecycle classification
- deployment/runtime configuration still needs exact current-main verification.

## Recommended priority

1. Run the full active Python test suite and exact PostgreSQL integration suite on the current main commit.
2. Remove runtime schema creation from repositories; make migrations the sole schema authority.
3. Build executable disposable PostgreSQL RLS tests with real roles/principal context.
4. Narrow broad exception handlers in canonical runtime paths.
5. Verify every deployment/startup entrypoint.
6. Resolve empty/placeholder active tests.
7. Perform evidence-based cleanup of remaining root legacy modules.
8. Continue Rust convergence only after the Python capability contracts and persistence/security gates are green.
