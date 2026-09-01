# Runtime Consumer Matrix — 2026-08-26

**Status:** Audit evidence / archive gate

## Scope

This matrix records evidence found while tracing runtime generations and duplicate trees. It is intentionally conservative: absence of a search hit is not proof that an external deployment consumer does not exist.

| Path / generation | Evidence found | Current classification | Archive gate |
|---|---|---|---|
| `src/web/canonical_app.py` | Current FastAPI assembly; canonical route tests target it | CANONICAL | Keep |
| `src/web/app.py` | Compatibility path; current Docker/Render/Procfile/entrypoint no longer require it | COMPATIBILITY | Keep until downstream imports are proven removable |
| `src/web.py` | Historical Flask runtime; deployment/audit documentation still references it; no current in-repo direct import evidence found | LEGACY / ARCHIVE CANDIDATE | Must verify external deployment consumers before archive |
| `janavani_v2/src/web/app.py` | Separate v2 tree with web code, Cargo/Dioxus and deployment material | LEGACY GENERATION | Requires subtree-level capability/import/deployment audit |
| `janavani_v3/` | Separate v3 tree with developer/deployment/Cargo material | LEGACY GENERATION | Requires subtree-level capability/import/deployment audit |

## Evidence and interpretation

- Search results show separate `janavani_v2` and `janavani_v3` trees; these are not automatically disposable because generation age does not prove replacement parity.
- Search for `from src.web import app` returned the compatibility file and documentation/test references but no additional direct import evidence in the searched index.
- Search for `src.web.py` returned audit/deployment documentation and `render.yaml`; this indicates historical deployment relevance but does not by itself prove current production reachability.
- The canonical runtime assembly is explicitly separated from the compatibility path.

## Required final archival evidence

Before deleting or archiving `src/web.py`, `janavani_v2/`, or `janavani_v3/`, verify all of the following:

1. No active deployment configuration points to the generation.
2. No CI workflow executes the generation.
3. No package/script entrypoint executes the generation.
4. No canonical runtime imports unique functionality from it.
5. No active client depends on its API/routes.
6. Any unique capability has a canonical replacement with behavioral evidence.
7. Tests covering retained behavior pass against the canonical implementation.
8. Documentation links/instructions have been migrated.
9. Historical evidence is preserved in Git history or an explicit archive record.
10. External provider/deployment consumers have been checked where repository evidence cannot establish absence.

## Decision

**Do not delete `src/web.py`, `janavani_v2/`, or `janavani_v3/` in this pass.**

They remain legacy/archive candidates until the final dependency and deployment evidence gates are satisfied.

## Principle

> Archive-first. Delete only after evidence. Never infer runtime reachability or irrelevance from directory naming alone.
