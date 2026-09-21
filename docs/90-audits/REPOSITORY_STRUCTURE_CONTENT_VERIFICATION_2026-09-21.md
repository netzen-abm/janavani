# Repository Structural Convergence Audit — 2026-09-21

## Scope

This audit was performed against the `main` tree before structural changes. The objective was to verify file content and references before moving or retiring any programming files.

## Verified decisions

| Area | Evidence-based disposition |
|---|---|
| `janavani_v2/` | Historical/parallel generation. Files were inspected before archival. No canonical runtime adoption was found. Archived under `archive/generations/janavani_v2/`. |
| `janavani_v3/` | Historical/experimental generation. Files were inspected before archival. No canonical runtime adoption was found. Archived under `archive/generations/janavani_v3/`. |
| `src/domain/*.py` | All inspected files were empty placeholders. Quarantined under `archive/legacy/quarantined/src/domain/`. |
| `src/models/*.py` | All inspected files were empty placeholders. Quarantined under `archive/legacy/quarantined/src/models/`. |
| `src/engine/` | All five files were inspected. The engine was either explicitly reserved/post-MVP or orphaned from active imports. Quarantined under `archive/legacy/quarantined/src/engine/`. |
| `src/workflow/` | Both files were inspected. They form an older workflow abstraction and were not referenced by the active canonical runtime. Quarantined under `archive/legacy/quarantined/src/workflow/`. |
| `src/web_mvp/` | **Retained.** A current test imports `src.web_mvp.services.api_client.JanavaniWebAPIClient`; the adapter targets the canonical API and verified identity assertion. |
| `src/services/` | **Not bulk-moved.** It is mixed: active compatibility adapters, fail-closed tombstones, and transitional implementations coexist. Each requires individual consumer migration evidence. |
| Root deployment/configuration | **Not rearranged yet.** Runtime/deployment ownership needs verification before movement. |

## Structural principle

Canonical direction:

    Surface Adapter
        ↓
    ProviderComposition
        ↓
    Canonical Capability
        ↓
    Domain / Security / Consent
        ↓
    Provider / Repository
        ↓
    Unit of Work / External Boundary

Historical generations are evidence sources, not competing runtimes.

## Archive-first rule

No verified historical implementation was destroyed. V2/V3 generations were first copied into the archive tree and then removed from their root locations. Empty/orphaned placeholder modules were moved to a quarantine archive rather than deleted.

## Verification note

The GitHub tree after the operation confirms:
- `janavani_v2/` root path is absent.
- `janavani_v3/` root path is absent.
- `archive/generations/janavani_v2/` exists.
- `archive/generations/janavani_v3/` exists.
- quarantined placeholder modules exist under `archive/legacy/quarantined/`.

Search results can retain historical/indexed references temporarily; those are documentation/history references and must be updated during documentation convergence.

## Next structural gate

Do not bulk-move `src/services/`, `src/web/`, deployment files, or documentation until their active consumers and ownership are individually verified.
