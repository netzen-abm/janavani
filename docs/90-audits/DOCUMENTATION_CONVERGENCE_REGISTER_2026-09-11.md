# Janavani — Documentation Convergence Register

**Status:** ACTIVE AUDIT REGISTER
**Date:** 11 September 2026

## Purpose

Track documentation convergence without destroying historical work or creating a second source of truth.

## Convergence completed in this pass

| Former location | Disposition | Current owner |
|---|---|---|
| `planning/DATABASE_CONTRACT.md` | Archived as superseded MVP contract | `docs/ARCHITECTURE.md` + `docs/ARCHITECTURE_DATA_BOUNDARY.md` |
| `planning/OFFICE_SCHEMA.md` | Archived as superseded MVP schema | Current authority/office capability documentation and implementation |
| `planning/DOCUMENT_CONTRACT.md` | Archived as superseded MVP contract | Active architecture/capability contracts |
| `planning/WORKFLOW_CONTRACT.md` | Archived as superseded MVP workflow | `docs/JANAVANI_MASTER_ARCHITECTURE.md` + active workflow contracts |
| `planning/ENGINEERING_CONSTITUTION.md` | Archived as superseded MVP constitution | `planning/ECOSYSTEM_ENGINEERING_CONSTITUTION.md` |
| `planning/ENGINEERING_PRINCIPLES.md` | Removed because file was empty | `docs/ARCHITECTURE_PRINCIPLES.md` |
| `planning/IDENTITY_ACCESS_TRUST_CONTRACT.md` | Consolidated | `docs/IDENTITY_ACCESS_TRUST.md` |
| `planning/IDENTITY_ACCESS_TRUST_IMPLEMENTATION_MAP.md` | Consolidated | `docs/IDENTITY_ACCESS_TRUST.md` |

## Content review findings

### Database contract / database design

The former MVP database documents correctly separated persistence from business logic, but their citizen/complaint scope was explicitly MVP-era. The current data-boundary architecture is broader and privacy-first. The old documents are therefore historical rather than active specifications.

### Office schema

The former office schema is a useful historical shape for the MVP office service, but it must not silently become the universal current authority model. Authority resolution now requires verified jurisdiction and destination semantics beyond a flat MVP office record.

### Document contract

The separation between conversation, document composition and PDF rendering is architecturally useful. The MVP file itself is archived because current document generation must also remain separate from submission, evidence and provenance concerns.

### Workflow contract

The state-driven workflow discipline remains useful, but the old complaint/RTI sequence is narrower than the current canonical civic Case lifecycle. It is archived rather than treated as the complete ecosystem workflow.

### Identity/access/trust

The former contract and implementation map overlapped substantially. They are now represented by one canonical active contract with implementation status kept explicit. `docs/AUTHENTICATION.md` remains a current repository-state note and must not become a competing architecture specification.

## Remaining review queue

The following areas require individual content review before any further move, rename or deletion:

- remaining `planning/*.md` files;
- `docs/architecture/*.md`;
- remaining non-archive `docs/*.md`;
- `docs/audits/` versus `docs/90-audits/`;
- `janavani_v2/` and `janavani_v3/` documentation;
- `archive/documentation/legacy/`;
- any root-level Markdown outside the canonical project entry set.

## Mandatory cleanup sequence

```text
Inventory
  → Read content
  → Classify owner/status
  → Compare competing documents
  → Merge unique current content
  → Update references
  → Archive
  → Verify
  → Delete only with evidence
```

## Non-negotiable rule

**Old does not mean useless. Duplicate does not mean identical. Archived does not mean deleted. Current documentation must be authoritative; historical documentation must remain traceable.**

## Verification requirement

Before PR #127 is merged, the final diff must be checked for broken references, contradictory active guidance, accidental deletion of historical material, and documentation that claims implementation or verification without evidence.
