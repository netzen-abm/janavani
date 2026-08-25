# Janavani Documentation Cleanup Register

**Status:** Active audit register  
**Branch:** `refactor/document-capability-convergence`  
**Rule:** Evaluate → Audit → Compare → Modify/Merge → Archive → Delete only with evidence

## Purpose

Track documentation consolidation without deleting historical material prematurely.

## Initial evidence set

The repository currently contains overlapping documentation families across `docs/`, `planning/`, root-level files, generation trees, and historical archives. Search evidence confirms dedicated documentation-convergence records already exist, including `DOCUMENTATION_INDEX.md`, `DOCUMENTATION_CONVERGENCE_AUDIT_2026-08-23.md`, `DOCUMENTATION_CORRECTION_NOTICE_2026-08-23.md`, and `DOCUMENTATION_CONVERGENCE_STATUS_2026-08-23.md`. fileciteturn664file7L36-L40 fileciteturn664file8L41-L45 fileciteturn664file9L46-L50 fileciteturn664file10L51-L55

The repository also has overlapping architecture families, including `ARCHITECTURE.md`, `ARCHITECTURE_PRINCIPLES.md`, `ARCHITECTURE_DECISIONS.md`, canonical API documents, runtime/client ownership, and capability maps. fileciteturn662file0L2-L2

## First-pass dispositions

| Family | Current disposition | Action |
|---|---|---|
| Source of truth / ecosystem authority | Canonical family | Keep; reconcile references |
| Master architecture / architecture principles | Canonical family | Keep; remove contradictions |
| Architecture decisions | Supporting canonical record | Expand/normalize ADR format; do not duplicate decisions |
| Capability registry | Canonical living registry | Keep as capability index |
| Capability repository/test/deployment map | Supporting/audit | Keep as evidence; update as implementation changes |
| API assembly / route ownership | Canonical supporting architecture | Keep; reconcile with actual code |
| Runtime/client ownership | Point-in-time canonical audit | Keep dated; replace with newer audit when evidence changes |
| Privacy architecture | Canonical privacy architecture | Keep; link safety/default gate |
| Privacy contract | Domain/capability contract | Keep; do not merge away semantics |
| Database contract/design | Domain/platform supporting docs | Compare and merge only where scopes overlap |
| Empty/near-empty planning files | Orphan candidates | Inspect references before action |
| Historical generation documents | Historical | Preserve in archive; never treat as active authority |
| Duplicate/overlapping documentation indexes | Merge candidates | Compare navigation coverage before consolidation |

## High-priority comparisons

### Architecture/governance

Compare:

- `docs/SOURCE_OF_TRUTH.md`
- `docs/ECOSYSTEM_CHARTER.md`
- `docs/JANAVANI_ECOSYSTEM_CHARTER.md`
- `docs/JANAVANI_MASTER_ARCHITECTURE.md`
- `docs/ARCHITECTURE.md`
- `docs/ARCHITECTURE_PRINCIPLES.md`
- `docs/ARCHITECTURE_DECISIONS.md`
- `planning/ARCHITECTURE_INDEX.md`
- engineering/founder/ecosystem constitution documents.

### Documentation navigation

Compare the existing documentation index, convergence audit/status/correction records, and the new `docs/DOCUMENTATION_STRUCTURE.md` before changing navigation links.

### Privacy and safety

Compare:

- `planning/PRIVACY_ARCHITECTURE.md`
- `planning/PRIVACY_CONTRACT.md`
- `docs/PRIVACY_SAFETY_BY_DESIGN.md`

The privacy architecture is the detailed data-boundary authority; the safety document is the cross-cutting safety/verification gate. Neither should be silently replaced by a summary document.

### Contracts and data

Compare database, document, service, workflow, data-boundary, storage-ownership and capability documents before merging. Contracts must retain normative requirements even if navigation is consolidated.

## Required evidence before archive/delete

A candidate may move from `DUPLICATE / MERGE CANDIDATE` to `ARCHIVE` only after:

- scope comparison;
- reference search;
- implementation relevance check;
- replacement identified;
- inbound links migrated or intentionally retained;
- historical value assessed.

A candidate may move from `ARCHIVE` to `DELETE` only after a separate review demonstrates that preservation is no longer required and the archive contains sufficient evidence.

## Implementation coupling rule

Whenever code is changed because of a documentation decision, the documentation change must be included in the same convergence workstream and must describe the implemented state accurately.

## Next register expansion

The next audit pass should enumerate every `.md`, `.mdx`, `.rst`, `.txt`, `.adoc`, architecture diagram/source, and documentation-like file outside generated/vendor/archive trees, then assign each a classification and target location under `docs/DOCUMENTATION_STRUCTURE.md`.
