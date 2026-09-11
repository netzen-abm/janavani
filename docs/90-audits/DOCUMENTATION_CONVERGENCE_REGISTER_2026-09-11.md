# JANAVANI — DOCUMENTATION CONVERGENCE REGISTER

**Date:** 11 September 2026
**Status:** ACTIVE AUDIT REGISTER
**Scope:** Markdown documentation in the Janavani repository

## 1. Purpose

Record the documentation review and prevent duplicate architecture, planning, contract and audit documents from becoming competing instructions.

## 2. Findings

### Canonical documentation

- `docs/JANAVANI_NORTH_STAR.md` — strategic destination.
- `docs/JANAVANI_ECOSYSTEM_CHARTER.md` — ecosystem identity/scope.
- `docs/SOURCE_OF_TRUTH.md` — canonical architectural rules.
- `docs/JANAVANI_MASTER_ARCHITECTURE.md` — detailed ecosystem architecture.
- `docs/ARCHITECTURE.md` — canonical system architecture.
- `docs/ARCHITECTURE_PRINCIPLES.md` — testable engineering invariants.
- `docs/JANAVANI_PRODUCT_LANDSCAPE.md` — product/capability landscape.
- `docs/CAPABILITY_REGISTRY.md` — capability inventory.
- `docs/DATA_CONTRACTS.md` — data contracts.
- `docs/MASTER_TASK_CHECKLIST.md` — canonical task inventory.
- latest dated status register — current execution evidence.

These documents have distinct owners and should not be merged into one oversized file merely to reduce file count.

### Consolidated in this pass

- `docs/DOCUMENTATION_INDEX.md` rewritten as the authority and organization map.
- `docs/PROJECT_MAP.md` rewritten as the current repository ownership map and stripped of obsolete MVP framing.
- `docs/DEVELOPER_GUIDE.md` rewritten as the current development entry guide.
- `docs/ARCHITECTURE_DECISIONS.md` rewritten as a concise ADR register rather than a second architecture specification.
- `planning/ARCHITECTURE_INDEX.md` converted into a deconfliction pointer; it no longer acts as an architecture authority.
- `docs/README.md` added as the documentation entry point.
- `docs/AI_HUMAN_DEVELOPER_CONTEXT.md` added as the concise cross-role orientation document.

### Duplicate/legacy candidates requiring further content review

1. `planning/OFFICE_SCHEMA.md` — MVP-labelled schema; compare against `docs/DATA_CONTRACTS.md` and current Authority/office models before archive or promotion.
2. `planning/DATABASE_CONTRACT.md` — MVP-labelled storage guidance; compare against current storage ownership/provider contracts before archive.
3. `planning/DOCUMENT_CONTRACT.md` — useful historical separation of builder/PDF responsibilities, but compare with current document capability before archive or promotion.
4. `planning/WORKFLOW_CONTRACT.md` — useful historical workflow model; compare with current workflow/civic-action contracts before archive.
5. `planning/PRIVACY_ARCHITECTURE.md` — substantive privacy material; compare with `docs/ARCHITECTURE_DATA_BOUNDARY.md` and current privacy contracts before deciding whether it remains a detailed planning specification or is consolidated.
6. `planning/SERVICE_CONTRACT.md` — MVP-labelled and potentially overlaps current service architecture; content review required.
7. `planning/SESSION_SCHEMA.md` — MVP-labelled; content review against current conversation/session state implementation required.
8. `planning/DATABASE_DESIGN.md` and related planning data documents — reconcile with current storage ownership and actual repositories.
9. `janavani_v3/*.md` — historical implementation generation; do not treat as current authority without runtime evidence.
10. `docs/archive/`, `docs/legacy/` and `archive/documentation/legacy/` — historical material; preserve unless demonstrably duplicate and safe to consolidate.

## 3. Dated evidence rule

Dated audit/status documents are not duplicates merely because they describe the same subject. They preserve point-in-time evidence and should be retained or moved into audit/history areas rather than rewritten into present-tense architecture.

## 4. Naming/organization recommendation

Use responsibility-based names for active documents and date-stamped names for audits/status evidence. Avoid names such as `v2`, `v3`, `final`, `new`, `latest` unless the document is explicitly historical and the name is unavoidable.

## 5. Safe cleanup sequence

```text
Inventory
  ↓
Read content
  ↓
Classify owner/status
  ↓
Compare with canonical documents
  ↓
Merge unique current content
  ↓
Update references
  ↓
Archive superseded material
  ↓
Verify links/imports/navigation
  ↓
Delete only with evidence
```

## 6. Important current contradiction removed

Older developer/project documents used MVP language that could be interpreted as shrinking Janavani's product boundary. The current documentation now consistently distinguishes the **complete ecosystem** from individual construction milestones.

## 7. Remaining work

The next documentation pass should review the full `planning/` directory and every non-archive Markdown file in `docs/` against this register, then archive or consolidate only where content and dependency evidence justify it.

**No historical document is to be deleted solely because it is old.**
