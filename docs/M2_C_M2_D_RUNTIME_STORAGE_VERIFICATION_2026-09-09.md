# JANAVANI — M2-C / M2-D STORAGE + RUNTIME VERIFICATION

**Date:** 9 September 2026  
**Scope:** Current `main` branch  
**Mode:** Evidence-based repository verification; no production database activation  
**Status:** M2-C partially verified; M2-D partially verified; live runtime evidence remains open

## 1. Executive result

The current repository has a coherent canonical Case persistence boundary, but it does **not** yet have enough evidence to claim production durable storage or live deployment verification.

The canonical storage rule is:

```text
CivicCase
  -> CivicCaseRepository
      -> provider adapter
          -> PostgreSQL / Supabase when explicitly configured
```

The repository intentionally keeps provider mechanics outside the domain. Binary evidence and generated documents remain separate from the Case row.

## 2. M2-C — Storage ownership verification

### 2.1 Canonical Case repository contract

`src/storage/repositories/civic_case.py` defines the provider-neutral `CivicCaseRepository` protocol with `save()` and `get()` operations. `InMemoryCivicCaseRepository` is explicitly process-local and is appropriate for tests/development, not a durable production authority.

### 2.2 PostgreSQL provider

`src/storage/repositories/postgres_civic_case.py` is the strongest current durable implementation. It uses Psycopg 3, accepts an injected connection factory or `JANAVANI_POSTGRES_DSN`, and uses the shared PostgreSQL Unit-of-Work boundary. Case creation/update, lifecycle events, evidence references and document references are persisted through one transaction boundary.

The provider implements optimistic concurrency and rejects stale versions. This is consistent with the canonical database contract.

### 2.3 Supabase provider

`src/storage/repositories/supabase_civic_case.py` remains a provider adapter, but its own documentation explicitly does not claim multi-table atomicity. It performs multiple client-side operations. Therefore it is **not yet eligible to replace the PostgreSQL Unit-of-Work provider as the production transactional authority** until a verified transaction/RPC boundary is added and tested.

### 2.4 Evidence/document ownership

The canonical schema and implementation specification state that Case persistence stores evidence/document references, not binary payloads. Evidence bytes and generated document artifacts belong to their respective storage/object-storage capability boundaries.

### 2.5 Consent boundary

Consent remains independently owned. The current Case aggregate stores consent references, while the PostgreSQL provider hydrates those references but does not manufacture durable consent records. Production activation must wait for the canonical Consent object/repository contract.

### 2.6 Schema readiness

`docs/architecture/POSTGRESQL_MIGRATION_DRAFT.sql` is explicitly marked review-only and not authorized for production execution. It defines the current relational draft but intentionally omits final RLS, legacy-data migration and production-specific configuration. Therefore no database migration is authorized by this verification pass.

### M2-C conclusion

**PARTIALLY VERIFIED.** Ownership boundaries are sufficiently clear for continued implementation. Production storage activation remains gated by canonical Identity/Consent/Evidence/Authority contracts, final schema/RLS review, disposable-database testing, restore testing and actual deployment configuration.

## 3. M2-D — Runtime/deployment verification

### 3.1 Canonical API assembly

`src/web/canonical_app.py` is the canonical FastAPI assembly and exposes `/`, `/liveness`, and `/version`.

`src/web/app.py` is only a compatibility import that delegates to the canonical assembly; it contains no independent business logic.

### 3.2 Render

`render.yaml` currently specifies a Python web service using:

```text
uvicorn src.web.canonical_app:app --host 0.0.0.0 --port $PORT
```

This is aligned with the canonical assembly and is the current repository-declared Render entry point.

### 3.3 Docker

The Dockerfile was corrected in this verification pass to invoke the canonical assembly directly:

```text
uvicorn src.web.canonical_app:app --host 0.0.0.0 --port 8000
```

This removes an unnecessary compatibility hop and prevents the container definition from drifting toward a different application generation.

`entrypoint.sh` already invoked the same canonical assembly.

### 3.4 Docker Compose

`docker-compose.yml` currently describes a broader local ecosystem including gateway, AI service, Redis, Ollama, Web MVP, admin UI and Dioxus tooling. It remains a **local ecosystem configuration, not verified production topology**. Its components need further convergence before it can be treated as the canonical deployment manifest.

### 3.5 Live runtime evidence

Repository configuration alone does not prove a deployed service is live. This review has **not** established live HTTP evidence for Render/Vercel or a running Docker container. Therefore `/liveness`, `/version`, authenticated civic-case operations, actual environment variables and configured providers remain unverified at runtime.

### 3.6 Full test execution

The repository contains `tests/test_canonical_app.py` and focused Case/storage tests, and the canonical test orchestrator requires Python, Rust core/application and Dioxus suites. A complete execution result for the current `main` commit has not been independently observed in this verification pass.

The successful Architecture Guard and Security CI runs previously recorded for the current convergence commit are valuable evidence, but they do not equal a full application test-suite pass.

## 4. Archive/consolidation decision

No additional storage/runtime implementation was archived or deleted solely because it appears older. Existing historical material remains subject to the archive-first rule. The current evidence is sufficient to identify the canonical Case storage boundary, but not sufficient to destroy alternative implementations that may contain irreplaceable migration or historical information.

## 5. Required next verification gates

1. Obtain actual runtime/deployment evidence for the Render development service, including `/liveness`, `/version` and the Case API.
2. Execute and record the full `run_all_tests.sh` suite for the exact current `main` commit.
3. Complete canonical Identity + Consent contracts before durable production Case activation.
4. Complete Evidence + Provenance ownership and local/original-preservation verification.
5. Perform final PostgreSQL schema/RLS review against a disposable database and restore test before production migration.
6. Verify Telegram against the same canonical Case lifecycle after the Web reference path is proven.

## 6. Status

| Gate | Result |
|---|---|
| Provider-neutral Case repository | VERIFIED |
| PostgreSQL Case adapter | IMPLEMENTED / VERIFYING |
| Shared PostgreSQL Unit-of-Work | VERIFIED IN REPOSITORY |
| Supabase atomic production boundary | NOT VERIFIED |
| Evidence/document binary ownership | VERIFIED BY CONTRACT |
| Consent durable ownership | NOT READY |
| Render repository entry point | VERIFIED IN CONFIG |
| Docker canonical entry point | VERIFIED / CORRECTED |
| Docker Compose production truth | NOT VERIFIED |
| Live deployment HTTP evidence | OPEN |
| Full Python/Rust/Dioxus test evidence | OPEN |
| Production database activation | NOT AUTHORIZED |

**M2-C:** PARTIALLY VERIFIED  
**M2-D:** PARTIALLY VERIFIED  
**Next frontier:** live/runtime evidence + full test execution, followed by Identity/Consent and the flagship Case → Evidence → Authority → Document → Review slice.
