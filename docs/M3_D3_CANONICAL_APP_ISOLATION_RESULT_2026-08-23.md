# JANAVANI — M3-D.3 CANONICAL APPLICATION-ROOT ISOLATION RESULT

**Date:** 23 August 2026  
**Phase:** M3-D.3  
**Mode:** CONTROLLED STRUCTURAL ISOLATION  
**Repository:** `netzen-abm/janavani`

## 1. Objective

Create a clean FastAPI assembly boundary without modifying or deleting the historical `src/web/app.py`.

## 2. Source verification

Immediately before this change, `src/web/app.py` was re-fetched at the M3-D design baseline. It creates a FastAPI application and later replaces the `app` symbol with a Flask application. fileciteturn406file0 fileciteturn407file0

The existing feedback, legislative, constitutional and land routers were also re-fetched before assembly. Their current public prefixes are:

```text
/api/v1/feedback
/api/v1/legislative
/api/v1/constitutional
/api/v1/land
```

fileciteturn411file0 fileciteturn408file0 fileciteturn409file0 fileciteturn410file0

## 3. Change made

Added:

```text
src/web/canonical_app.py
```

The new module:

- creates exactly one FastAPI application;
- imports domain routers directly;
- registers feedback, legislative, constitutional and land routers;
- exposes `/liveness`;
- exposes `/version`;
- does **not** import `src.web.app`;
- does **not** modify the historical runtime.

This establishes a clean candidate application root while keeping the legacy implementation intact.

## 4. Important limitation

The agent/SOS router has deliberately **not** been included yet.

Reason: the existing agent implementation contains authentication/token handling, Redis access and SOS behavior that require a separate security-controlled extraction. The canonical root must not accidentally imply that SOS is production-approved merely by registering it.

## 5. Current topology

```text
                         Clients
                            │
                            ▼
                 src/web/canonical_app.py
                            │
        ┌───────────┬───────┼───────────┬───────────┐
        ▼           ▼       ▼           ▼           ▼
    feedback   legislative constitutional land    platform
        │           │       │           │        liveness/version
        ▼           ▼       ▼           ▼
     existing    existing existing   existing
     router      router   router     router
```

Historical:

```text
src/web/app.py
     │
     ├── historical FastAPI generations
     └── historical Flask generation
```

The historical module remains untouched.

## 6. Why this is safer

This creates an importable canonical boundary without attempting a mass rewrite of the legacy application. It allows route registration and application startup to be tested independently before production deployment configuration is changed.

## 7. Not yet done

The following are intentionally NOT claimed complete:

- agent route migration;
- SOS migration;
- authentication consolidation;
- secret removal;
- storage adapter extraction;
- service-layer extraction;
- production container cutover;
- route parity certification;
- CI integration for the new canonical root.

## 8. Next gate — M3-D.4

Before further route extraction:

1. Add a minimal route-registration/import test for `src.web.canonical_app`.
2. Verify the four registered domain route prefixes and `/liveness`/`/version`.
3. Run the targeted test suite if available.
4. Only after that, design the controlled **agent/SOS extraction**, with authentication separated from emergency orchestration.

## 9. Status

**M3-D.3: COMPLETE — STRUCTURAL ISOLATION**  
**Legacy `src/web/app.py` modified:** NO  
**Routes deleted:** NO  
**Historical files archived:** NO  
**Production deployment changed:** NO  
**Canonical FastAPI candidate:** `src.web.canonical_app:app`

**END OF DOCUMENT**
