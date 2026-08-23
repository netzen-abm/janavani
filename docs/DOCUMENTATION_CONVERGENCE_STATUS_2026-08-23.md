# JANAVANI — DOCUMENTATION CONVERGENCE STATUS

**Date:** 23 August 2026
**Purpose:** Control document cleanup so obsolete MVP-era framing is not mistaken for current Janavani direction.

## Current canonical chain

1. `docs/JANAVANI_ECOSYSTEM_CHARTER.md`
2. `docs/JANAVANI_NORTH_STAR.md`
3. `docs/SOURCE_OF_TRUTH.md`
4. `docs/JANAVANI_MASTER_ARCHITECTURE.md`
5. `docs/JANAVANI_PRODUCT_LANDSCAPE.md`
6. `ROADMAP.md`
7. `docs/CAPABILITY_REGISTRY.md`
8. `docs/MASTER_TASK_CHECKLIST.md`
9. Active `planning/` contracts
10. Code/tests/deployment evidence

## Completed in this cleanup pass

- [x] Create current ecosystem charter.
- [x] Replace README MVP framing.
- [x] Replace ROADMAP MVP framing.
- [x] Replace North Star MVP/current-priority framing.
- [x] Replace Source of Truth MVP/current-priority framing.
- [x] Replace Product Landscape MVP framing.
- [x] Create ecosystem engineering constitution.
- [x] Create ecosystem acceptance/verification standard.
- [x] Archive former MVP Constitution.
- [x] Archive former MVP Acceptance Test.
- [x] Archive former MVP Release Baseline.

## Remaining documentation convergence

### Active documents requiring review

- [ ] `docs/JANAVANI_MASTER_ARCHITECTURE.md`
- [ ] `docs/PROJECT_MAP.md`
- [ ] `docs/ARCHITECTURE.md`
- [ ] `planning/PRODUCT_REQUIREMENTS.md`
- [ ] `planning/ARCHITECTURE_INDEX.md`
- [ ] `planning/DATABASE_CONTRACT.md`
- [ ] `planning/DOCUMENT_CONTRACT.md`
- [ ] `planning/WORKFLOW_CONTRACT.md`
- [ ] `planning/SERVICE_CONTRACT.md`
- [ ] `planning/PRIVACY_CONTRACT.md`
- [ ] `planning/SESSION_SCHEMA.md`
- [ ] `planning/OFFICE_SCHEMA.md`
- [ ] `planning/FOUNDER_CONSTITUTION.md`
- [ ] `docs/RELEASE_1_CHECKLIST.md`
- [ ] deployment/runbook documents
- [ ] V2/V3 architecture documents
- [ ] root-level architecture indexes

### Historical documents

Dated audits and legacy design records should remain available as evidence. They should not be rewritten to match the current architecture. If a historical document is actively referenced as current direction, replace that reference with the current canonical document.

## Rule for cleanup

A document is **ACTIVE** only if it describes current architecture, current contracts, current product direction, or current verification status.

A document is **HISTORICAL** if it records an earlier design, experiment, audit, or decision.

A historical document may remain unchanged when it is useful evidence. It must not compete with current active documentation.

## Next documentation pass

The next pass must review the remaining active `.md` files one by one against the Ecosystem Charter and Source of Truth, classify each as:

`KEEP / UPDATE / REPLACE / ARCHIVE`

Only after this pass is complete should programming changes resume.
