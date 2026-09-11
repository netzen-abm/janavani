# JANAVANI — DOCUMENTATION INDEX & AUTHORITY MAP

**Status:** LOCKED — DOCUMENTATION ORGANISATION STANDARD
**Version:** 2.0
**Date:** 11 September 2026

This index prevents contradictory documents, duplicate audits, stale implementation instructions and accidental use of historical material.

## 1. Authority hierarchy

When documents conflict, use this order:

1. `docs/JANAVANI_NORTH_STAR.md` — strategic destination and civic purpose
2. `docs/JANAVANI_ECOSYSTEM_CHARTER.md` — locked identity and ecosystem scope
3. `docs/SOURCE_OF_TRUTH.md` — canonical architectural rules
4. `docs/JANAVANI_MASTER_ARCHITECTURE.md` — detailed ecosystem architecture
5. `docs/ARCHITECTURE.md` — canonical system-layer architecture
6. `docs/ARCHITECTURE_PRINCIPLES.md` — testable engineering invariants
7. `docs/JANAVANI_PRODUCT_LANDSCAPE.md` — capability/product landscape
8. `ROADMAP.md` — construction sequence
9. `docs/CAPABILITY_REGISTRY.md` + active `planning/` contracts — capability/data specifications
10. `docs/MASTER_TASK_CHECKLIST.md` — canonical task inventory
11. Latest dated status register — current execution status/evidence
12. Implementation, tests, CI and deployment evidence — what is actually verified
13. `docs/AI_HUMAN_DEVELOPER_CONTEXT.md` — concise orientation across all of the above; it does not override them

Dated audits preserve historical evidence. They do not override current canonical documents unless explicitly adopted.

## 2. Documentation roles

### Root

Keep only project entry documents and operational configuration. Avoid new architecture notes at root.

### `docs/`

Active canonical architecture, product, governance, security, operations, audits and evidence references.

### `docs/architecture/`

Focused active architecture specifications that have a distinct technical owner and do not duplicate `SOURCE_OF_TRUTH.md` or `JANAVANI_MASTER_ARCHITECTURE.md`.

### `docs/research/`

Research and external-system learning. Research is not product specification unless adopted into canonical documentation.

### `docs/90-audits/`

Current audit registers and audit-specific evidence.

### `planning/`

Active detailed engineering contracts/specifications. Planning material must have a clear relationship to canonical architecture. Historical/MVP-only planning documents must not remain active merely because they are technically detailed.

### `archive/`

Historical, superseded or deprecated documentation retained for traceability. Archived documents are not current instructions.

### `janavani_v2/` and `janavani_v3/`

Historical/parallel implementation trees. Their documentation is historical unless current repository/runtime evidence explicitly adopts a component.

## 3. Naming standard

- Canonical: stable descriptive names.
- Current status/audit: `NAME_YYYY-MM-DD.md`.
- Focused architecture: descriptive responsibility-based name under `docs/architecture/`.
- Research: descriptive topic under `docs/research/`.
- Historical: archive under the appropriate `archive/` subtree.
- Avoid multiple files that are merely alternate versions of the same architecture, roadmap or contract.

## 4. Required status vocabulary

Use one of:

`CANONICAL / ACTIVE / LOCKED / IN PROGRESS / DESIGN COMPLETE / VERIFYING / EVIDENCE / HISTORICAL / SUPERSEDED / ARCHIVED`

Do not use `complete`, `fully implemented` or `production ready` merely because source or documentation exists.

## 5. Non-duplication workflow

Before creating or renaming a Markdown document:

1. Read this index.
2. Search the repository for the subject and key terms.
3. Identify all competing documents.
4. Read the relevant candidates before deciding.
5. Select one canonical owner.
6. Merge useful unique content into the owner where appropriate.
7. Archive superseded documents with historical value preserved.
8. Update links/references.
9. Record the change in the documentation cleanup register.

## 6. Historical evidence rule

Do not rewrite a dated audit to make the past appear consistent with the present. Correct current guidance separately and preserve the historical record.

## 7. MVP terminology rule

Janavani is a complete ecosystem. MVP-era documents are historical unless explicitly retained as a current construction milestone. The word `MVP` must not be used to shrink ecosystem scope.

## 8. Current convergence finding

The repository currently contains several overlapping architecture/documentation generations, including root-level canonical documents, focused architecture documents, historical planning contracts and legacy trees. This is manageable but requires continued convergence.

Examples requiring controlled reconciliation include:

- `docs/ARCHITECTURE.md` and `docs/JANAVANI_MASTER_ARCHITECTURE.md` — both active, with distinct detail levels;
- `docs/ARCHITECTURE_DECISIONS.md` — retained as an ADR index and should grow rather than duplicate architecture prose;
- `planning/ARCHITECTURE_INDEX.md` — legacy planning index that still references MVP-era contracts;
- `planning/*_CONTRACT.md` files labelled MVP-era — candidates for reconciliation into active contracts or archive after content review;
- `docs/architecture/` — active focused specifications; must not become a second uncontrolled source of truth;
- `docs/audits/` and `docs/90-audits/` — must be consolidated by purpose over time;
- `docs/archive/`, `docs/legacy/` and root `archive/documentation/legacy/` — archive locations should be rationalised without losing historical evidence.

## 9. Current active orientation

For AI agents and developers, start with `docs/AI_HUMAN_DEVELOPER_CONTEXT.md`, then follow the authority hierarchy above.

The core invariant is:

> **Build Janavani as one coherent ecosystem with shared infrastructure, reusable capabilities and independent interfaces. Let citizens choose capabilities and surfaces; never confuse user choice with ecosystem omission.**

## 10. Cleanup rule

No destructive documentation cleanup is complete until links, references, repository navigation and historical traceability have been checked. Archive first. Delete only after replacement, dependency/reference and historical-value evidence.
