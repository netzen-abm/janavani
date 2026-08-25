# Janavani — Repository Convergence Audit

**Date:** 25 August 2026  
**Status:** ACTIVE — implementation convergence and verification  
**Scope:** repository structure, runtime entry points, duplicated/overwritten programming files, CI duplication, documentation authority and safe convergence actions.

## 1. Audit basis

This audit incorporates the current repository state and the project direction established in the existing canonical documentation and prior project review context.

The repository's current architectural direction is capability-first: shared platform capabilities are consumed by independent interfaces. The canonical architecture explicitly states that historical trees do not authorize duplicate implementations and that code removal requires import, runtime, test and documentation verification.

## 2. Confirmed critical finding — corrupted web application assembly

`src/web/app.py` contained multiple concatenated generations of application code in one Python module. The file repeatedly redefined `app`, routers, authentication, request models and endpoints, and even switched framework identity from FastAPI to Flask before continuing with more FastAPI generations.

This was not ordinary legacy compatibility code. It was an overwrite/append corruption pattern capable of making runtime behavior depend on whichever definition occurred last in the file.

The repository already had `src/web/canonical_app.py` as the intended FastAPI assembly boundary. Therefore the safe convergence action was to replace `src/web/app.py` with a small compatibility module that imports the canonical application instead of deleting the historical path immediately.

## 3. Confirmed critical finding — corrupted Dockerfile

`Dockerfile` contained two unrelated `FROM` blocks. The second block superseded the first Docker build stage as the final image and launched `api.agent_api:app`, while the first block attempted to launch `src.web.app:app`.

This represented competing runtime generations in one deployment artifact.

The Dockerfile has been converged to one Python 3.11 runtime using the compatibility entry point `src.web.app:app`, which delegates to `src.web.canonical_app`.

## 4. CI convergence finding

The repository contains multiple generic Python CI workflows with overlapping responsibilities. `ci.yml` is already the stronger canonical test orchestrator because it performs Python compilation and calls `run_all_tests.sh`.

`python-app.yml` and `python-package.yml` independently install pytest/flake8 and execute broad `pytest` runs. `django.yml` is particularly suspect because it invokes `manage.py`, while no repository-root `manage.py` is currently present.

These workflows should not be treated as authoritative until their historical purpose and recent run history are verified. The next convergence pass should consolidate obsolete generic workflows rather than maintaining several competing definitions of Python correctness.

## 5. Canonical test direction

`run_all_tests.sh` is the repository's declared canonical validation orchestrator. It runs the Python test suite and conditionally runs the Rust/Dioxus suite when `src/web_dioxus/Cargo.toml` exists.

Future CI convergence should prefer this orchestrator for repository-level validation and keep specialized workflows only where they test a genuinely independent capability or deployment artifact.

## 6. Documentation direction

The repository already establishes a documentation authority chain beginning with the North Star and Ecosystem Charter, followed by Constitutional Governance, Source of Truth, Master Architecture, Product Landscape, Roadmap, Master Task Checklist and Capability Registry.

Dated audits and engineering records should provide evidence rather than become competing architectural authorities. Superseded material should be archived once replacement and references are verified.

## 7. Changes made in this pass

### Changed

- Replaced the corrupted `src/web/app.py` with a compatibility entry point delegating to `src.web.canonical_app`.
- Replaced the two-generation `Dockerfile` with one canonical web/API runtime definition.
- Added this audit record to preserve the convergence evidence and prevent repeating the same investigation.

### Deliberately not deleted yet

- Historical API/POC implementation under `api/`.
- Generic/legacy CI workflow files.
- Other historical application trees.
- Existing dated architecture/audit documents.

Deletion requires dependency, import, workflow-run, deployment and documentation verification.

## 8. Next verification pass

1. Enumerate all Python/Rust/JS/TS source files and detect duplicate symbols and near-identical modules.
2. Trace imports into legacy and canonical trees.
3. Compare all API routers and route ownership against the canonical route map.
4. Audit workflow triggers and recent run history to identify redundant CI.
5. Audit tests for duplicated generations and false-positive existence tests.
6. Reconcile dated documentation into current authority plus evidence/archive categories.
7. Verify Docker, Procfile and deployment configurations against the canonical runtime boundary.
8. Run the canonical test suite after the runtime convergence changes.

## 9. Decision rule

No file is considered obsolete merely because a newer file exists. A removal decision requires evidence of replacement, dependency safety, runtime safety, test coverage and documentation reconciliation.
