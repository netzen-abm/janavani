# Janavani — Canonical Runtime Map

**Date:** 27 August 2026  
**Branch:** `refactor/case-capability-kernel`  
**Status:** working map; update as repository evidence changes.

## Purpose

This document separates the repository into canonical runtime, active supporting code, compatibility boundaries, scaffolds/future work, historical generations, and archive candidates. Classification requires repository evidence; filenames alone are insufficient.

## Current canonical path

```text
Case
  -> Evidence
  -> Authority
  -> Document
  -> Submission
  -> Tracking
  -> Web
```

Current implemented kernel components:

- `src/domain/case.py`
- `src/domain/evidence.py`
- `src/domain/authority.py`
- `src/storage/evidence_repository.py`
- `src/services/authority_service.py`
- `src/web/canonical_app.py`
- canonical Case/Evidence/Authority tests

## Runtime boundaries

| Component | Classification | Evidence / rationale |
|---|---|---|
| `src/web/canonical_app.py` | CANONICAL_PRODUCTION | Current FastAPI assembly and runtime entry point |
| `src/web/app.py` | COMPATIBILITY | Thin delegation boundary into canonical app |
| `src/domain/case.py` | CANONICAL_PRODUCTION | Active case lifecycle/domain contract |
| `src/domain/evidence.py` | CANONICAL_PRODUCTION | Active evidence contract with provenance/status |
| `src/domain/authority.py` | CANONICAL_PRODUCTION | Active source-backed authority contract |
| `src/storage/evidence_repository.py` | ACTIVE_SUPPORTING | Persistence boundary for Evidence |
| `src/services/authority_service.py` | ACTIVE_SUPPORTING | Directory/provider adapter into Authority |
| Telegram office selection | ACTIVE_SUPPORTING | Migrated from legacy office service to Authority |
| `src/services/office_service.py` | REMOVED | Superseded after consumer migration |
| `.github/workflows/verify-crate.yml` | REMOVED | Confirmed empty placeholder |
| `.github/workflows/python-package-conda.yml` | REMOVED | Broken legacy workflow; referenced missing `environment.yml` and failed before tests |

## CI truth findings

The canonical `ci.yml` runs Python 3.12, installs `requirements.txt`, compiles `src`, and invokes `run_all_tests.sh`. `run_all_tests.sh` is the repository's canonical test orchestrator and runs the Python suite plus the Rust/Dioxus suite when `src/web_dioxus/Cargo.toml` exists.

The older `python-package-conda.yml` unconditionally called `conda env update --file environment.yml`, but `environment.yml` is absent from the branch. A real GitHub Actions run on commit `f6182db788a2fdb50f0791384b3506f3491e5d42` failed at dependency installation with `EnvironmentFileNotFound` before lint or pytest. It was removed rather than repaired as a second dependency-management generation.

`startup-check.yml` remains a migration target. Its script inspects `src.web`, `src.bot_messenger`, `src.bot_whatsapp`, and `src.main`, and declares success if it finds any Flask-style `app`. The canonical Web runtime is FastAPI in `src.web.canonical_app`. This makes the current startup check insufficient as the authoritative application health gate. It should be replaced by a canonical FastAPI import/liveness check.

## Runtime truth finding

`src/main.py` is an executable-looking historical smoke script, but its imports (`tools.*`, `legal_brain`) do not resolve to files at those paths on the current branch. It is therefore classified as a **BROKEN/LEGACY entry point candidate**, not a canonical runtime entry point. The canonical web entry point is `src.web.canonical_app:app`.

## Historical generations

### `janavani_v2/`

Classified as **HISTORICAL_GENERATION** pending a complete dependency/deployment proof of current use. It contains an independent Rust/Dioxus application/build/test structure and deployment tooling.

### `janavani_v3/`

Classified as **HISTORICAL_GENERATION** pending the same proof. It contains an independent Rust/Dioxus application/build/test/deployment structure.

### `archive/`

Classified as **ARCHIVED_LEGACY** unless a current consumer is discovered. Archive contents must not be imported into the canonical runtime.

## Scaffold / placeholder inventory

The following root domain modules were confirmed empty on the audited branch/main lineage and are therefore **EMPTY_PLACEHOLDER**, not automatically obsolete:

- `src/domain/citizen.py`
- `src/domain/department.py`
- `src/domain/document.py`
- `src/domain/issue.py`
- `src/domain/location.py`
- `src/domain/remedy.py`
- `src/domain/submission.py`
- `src/domain/office.py`

`src/domain/evidence.py` is no longer a placeholder; it is canonical on the refactor branch.

## Dependency truth

`requirements.txt` contains both FastAPI and Flask. The canonical container launches FastAPI, while the Messenger and WhatsApp webhook modules are genuine Flask transport surfaces. Flask therefore remains justified for the current multi-surface repository until those transports are migrated or intentionally isolated.

## Rules for future classification

1. Do not delete by filename or age alone.
2. Prove active consumers before removal.
3. Treat historical generations as real code unless proven otherwise.
4. Keep compatibility layers thin and explicit.
5. Keep capability/domain logic provider-neutral.
6. Every canonical capability must have executable tests.
7. Update this map when a component changes classification.
