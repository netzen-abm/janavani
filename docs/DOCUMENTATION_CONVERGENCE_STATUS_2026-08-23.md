# JANAVANI — DOCUMENTATION CONVERGENCE STATUS

**Date:** 23 August 2026
**Purpose:** Control document cleanup so obsolete MVP-era framing is not mistaken for current Janavani direction.

## Current canonical chain

1. `docs/JANAVANI_NORTH_STAR.md`
2. `docs/JANAVANI_ECOSYSTEM_CHARTER.md`
3. `docs/SOURCE_OF_TRUTH.md`
4. `docs/JANAVANI_MASTER_ARCHITECTURE.md`
5. `docs/JANAVANI_PRODUCT_LANDSCAPE.md`
6. `ROADMAP.md`
7. `docs/CAPABILITY_REGISTRY.md` + active `planning/` contracts
8. `docs/MASTER_TASK_CHECKLIST.md`
9. `docs/MASTER_TASK_CHECKLIST_STATUS_2026-08-23.md`
10. Actual code/tests/CI/deployment evidence

## Completed in the current documentation convergence

- [x] Ecosystem identity and non-MVP scope established.
- [x] README reconciled with full ecosystem direction.
- [x] ROADMAP reconciled with full ecosystem direction.
- [x] Ecosystem Charter established as current identity/scope authority.
- [x] Source of Truth established as canonical architecture rule set.
- [x] Canonical `docs/ARCHITECTURE.md` replaced the old MVP-era architecture constitution.
- [x] Documentation Index created with authority hierarchy and ambiguity rules.
- [x] AI operations guide reconciled with current test/evidence discipline.
- [x] Obsolete root architecture/website/orchestration/runbook notes moved to `archive/documentation/legacy/`.
- [x] Historical MVP Constitution, acceptance and release-baseline material remains archived rather than competing with current direction.
- [x] Master checklist remains the control mechanism for task/subtask status.

## Remaining documentation convergence

The repository still contains many active and historical `.md` files. They must be reviewed **without blindly rewriting historical evidence**.

### Next review set

- `docs/JANAVANI_MASTER_ARCHITECTURE.md`
- `docs/PROJECT_MAP.md`
- `planning/PRODUCT_REQUIREMENTS.md`
- `planning/ARCHITECTURE_INDEX.md`
- `planning/DATABASE_CONTRACT.md`
- `planning/DOCUMENT_CONTRACT.md`
- `planning/WORKFLOW_CONTRACT.md`
- `planning/SERVICE_CONTRACT.md`
- `planning/PRIVACY_CONTRACT.md`
- `planning/SESSION_SCHEMA.md`
- `planning/OFFICE_SCHEMA.md`
- `planning/FOUNDER_CONSTITUTION.md`
- `docs/RELEASE_1_CHECKLIST.md`
- V2/V3 architecture documentation
- deployment/developer/contribution documents

Each document receives one classification:

`KEEP / UPDATE / REPLACE / ARCHIVE`

## Historical-document rule

Dated audits, experiment records and superseded decisions remain evidence. They must not be rewritten merely to agree with today's architecture. If an old document is referenced as current direction, the reference must be corrected.

## Ambiguity rule

If two active documents appear to define the same concept, the higher document in the canonical chain wins. The lower document must either be updated to defer to the higher authority or be archived if it has no independent current purpose.

## No-programming gate

Documentation convergence is not considered finished until the active documentation set has been reviewed sufficiently to establish:

- one product identity;
- one architecture authority;
- one roadmap;
- one master checklist with subtasks;
- clear current-vs-historical status;
- no active MVP product-boundary language;
- no duplicate current architecture authorities;
- explicit links/ownership for contracts and evidence.

Only then should broad programming/convergence work proceed.
