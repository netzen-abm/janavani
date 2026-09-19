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


## 2026-09-19 convergence pass — product-centre decision

### Decision

The previous proposal to make Janavani a universal government-service login/credential layer is **rejected as a primary product direction**. It remains only an external-service integration/handoff concern.

The product-centre rebaseline is recorded in:

- `docs/strategy/JANAVANI_CIVIC_CASE_PRODUCT_SPINE.md`

The existing canonical documents already converge on the same underlying lifecycle:

`Citizen Reality → Understanding → Evidence/Context → Correct Authority → Lawful Civic Action → Submission/Communication → Government Response → Tracking → Follow-up → Outcome → Accountability → Public Learning`.

The new product-spine document therefore consolidates interpretation rather than creating a competing architecture.

### Confirmed canonical family

The following documents were inspected against the current documentation authority hierarchy and are retained as active/canonical sources for their respective scopes:

- `docs/JANAVANI_NORTH_STAR.md` — strategic destination
- `docs/JANAVANI_ECOSYSTEM_CHARTER.md` — ecosystem identity/scope
- `docs/SOURCE_OF_TRUTH.md` — architectural authority
- `docs/JANAVANI_MASTER_ARCHITECTURE.md` — detailed architecture
- `docs/ARCHITECTURE.md` — system architecture
- `docs/ARCHITECTURE_PRINCIPLES.md` — engineering invariants
- `docs/JANAVANI_PRODUCT_LANDSCAPE.md` — product/capability landscape
- `docs/IDENTITY_ACCESS_TRUST.md` — identity/access/trust
- `docs/ARCHITECTURE_DATA_BOUNDARY.md` — data boundary
- `docs/CAPABILITY_REGISTRY.md` and `docs/architecture/CAPABILITY_REGISTRY.md` — capability registry family requiring reconciliation of ownership/navigation
- `docs/MASTER_TASK_CHECKLIST.md` — task authority
- `docs/architecture/CANONICAL_CIVIC_ACTION_SPINE.md` — civic action composition
- `docs/architecture/SHARED_CAPABILITY_SPINE_PLAN.md` — shared capability convergence
- `docs/architecture/CIVIC_CASE_DATABASE_CONTRACT.md` — durable case persistence contract
- `docs/architecture/CASE_LIFECYCLE_SEMANTICS.md` — lifecycle semantics
- `docs/architecture/CAPABILITY_GATEWAY_CONTRACT.md` — surface-neutral capability composition
- `docs/architecture/CONSEQUENTIAL_OPERATION_GATE.md` — authorization/consent/approval boundary

### High-confidence overlap / reconciliation targets

| Family | Finding | Disposition |
|---|---|---|
| Documentation index | `docs/DOCUMENTATION_INDEX.md` is explicitly LOCKED and already defines the authority hierarchy. | Canonical; do not replace |
| North Star / Charter / Source of Truth | Strongly aligned on ecosystem identity and citizen-government loop. | Retain as distinct scopes |
| Master architecture / Architecture / Principles | Overlapping but complementary; detailed content should not be duplicated. | Reconcile references, not wholesale merge |
| Product Landscape / new Civic Case spine | Product Landscape is broader; Civic Case spine makes the existing lifecycle the explicit product centre. | Retain both; link spine from product orientation |
| Capability Registry | Two registry paths exist. | Verify ownership and make one navigation/canonical owner explicit |
| Case lifecycle / Civic Action Spine / Case DB contract | Complementary: semantics, composition, persistence. | Retain distinct contracts |
| Capability Gateway / Consequential Operation Gate | Complementary: invocation boundary vs side-effect control. | Retain distinct contracts |
| External tool reuse | Current main does not yet contain PR #197's proposed document; it remains an open draft proposal. | Do not treat as main authority until merged |
| Dated audits/status reports | Point-in-time evidence. | Preserve; never rewrite to current state |
| `janavani_v2/`, `janavani_v3/` docs | Generation-specific/historical unless current runtime evidence proves adoption. | Historical; archive-first |
| `archive/` docs | Historical evidence. | Preserve; not active authority |

### Inventory coverage

The 2026-09-19 GitHub Markdown inventory search identified root, `docs/`, `planning/`, `janavani_v2/`, `janavani_v3/`, `archive/`, and source-adjacent documentation files. The inventory includes the existing canonical set, dated audits, architecture contracts, security documents, planning documents and historical generation documentation.

No destructive deletion is authorized by this pass.

### Remaining verification rule

Filename-based classification is not sufficient for final archive/delete decisions. Before any document is archived:

1. read the complete candidate;
2. compare unique normative content against its proposed owner;
3. search inbound references;
4. verify implementation/runtime relevance;
5. migrate useful unique content;
6. update navigation;
7. preserve historical provenance;
8. re-run repository-wide reference search.

This register therefore records **convergence decisions and evidence-backed candidates**, not permission for bulk deletion.
