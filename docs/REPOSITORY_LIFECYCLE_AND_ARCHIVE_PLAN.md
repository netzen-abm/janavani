# JANAVANI — REPOSITORY LIFECYCLE & ARCHIVE PLAN

**Status:** ACTIVE — CONTROLLED CONVERGENCE  
**Date:** 24 August 2026  
**Scope:** Documentation and programming-file reconciliation while App + DApp are built first.

## Purpose

Janavani contains multiple implementation generations, documentation generations, experiments, deployment templates and duplicated architectural material. The objective is **not** to delete aggressively. The objective is to establish one understandable canonical implementation while preserving historical evidence and useful research.

## Governing lifecycle

```text
DISCOVER
  ↓
VERIFY REFERENCES
  ↓
VERIFY RUNTIME / TESTS
  ↓
CLASSIFY
  ├── KEEP / CANONICAL
  ├── MODIFY / REFACTOR
  ├── ADD / FILL GAP
  ├── EXPERIMENTAL
  ├── DEPRECATE
  └── ARCHIVE
  ↓
UPDATE INDEXES + LINKS
  ↓
RUN REGRESSION
```

**Deletion is not the default.** Archive first; delete only after an explicit retention decision.

## Current repository findings

The existing reconciliation audit describes the repository as structurally rich but architecturally divergent, with a root implementation plus `janavani_v2` and `janavani_v3` parallel workspaces. It specifically recommends controlled convergence and says not to delete those workspaces until references, runtime, tests, deployment and canonical ownership are established. citeturn857file0

The documentation index already establishes `docs/`, `planning/`, and `archive/` responsibilities and an archive-first cleanup policy. citeturn858file0

## Classification matrix

| Area / item | Initial classification | Action |
|---|---|---|
| Root `src/` | KEEP / CANONICAL CANDIDATE | Continue runtime/import audit |
| Root tests | KEEP | Expand coverage for App/DApp isolation |
| `janavani_v2/` | HISTORICAL / PARALLEL | Do not delete; map useful modules and references |
| `janavani_v3/` | EXPERIMENTAL / PARALLEL | Do not delete; determine whether client components should migrate into canonical App architecture |
| `src/web_dioxus/` | KEEP / VERIFY | Inspect as possible Web/DApp client foundation |
| `docs/JANAVANI_APP_DAPP_FIRST_BUILD_PLAN.md` | ACTIVE | Keep; align with ecosystem action plan |
| `docs/JANAVANI_APP_DAPP_ECOSYSTEM_ACTION_PLAN.md` | CONTROL DOCUMENT | Keep as implementation/decision log |
| `docs/RELEASE_1_CHECKLIST.md` | ACTIVE MILESTONE CHECKLIST | Keep; filename is historical/misleading and should eventually be renamed through a controlled move |
| `docs/ARCHITECTURE.md` | CANONICAL CANDIDATE | Reconcile against master architecture |
| `docs/architecture.txt` | ARCHIVE CANDIDATE | Compare content first; archive if duplicate/superseded |
| `README.md` | KEEP / MODIFY | Reconcile product scope and current implementation status |
| `ROADMAP.md` | KEEP / MODIFY | Align first-build ordering with App + DApp while retaining full ecosystem |
| `docs/WIKI_HOME.md` | KEEP / MODIFY | Make it navigation to current canonical documentation |
| `docs/PROJECT_MAP.md` | KEEP / MODIFY | Make implementation map evidence-based |
| `docs/CAPABILITY_REGISTRY.md` | KEEP / CANONICAL | Extend with App/DApp independence and capability health contracts |
| `docs/DATA_CONTRACTS.md` | KEEP / CANONICAL | Use as shared contract basis |
| `planning/` contracts | KEEP / VERIFY | Remove contradictions only after comparison |
| Dated audits | KEEP | Preserve historical evidence; link latest unresolved delta |
| Existing `archive/` | KEEP | Continue archive-first policy |
| Root `.tar.gz` | REVIEW / ARCHIVE CANDIDATE | Verify contents and provenance before action |
| Root `Future Platform Engineering & Architectural Recommendations` | REVIEW | Convert useful content into canonical docs, then archive if duplicate |
| Excess CI templates | REVIEW | Keep security/dependency/test workflows; disable/archive unrelated templates only after workflow-usage audit |
| `janavani_v2`/`v3` duplicate deployment scripts | REVIEW | Do not execute as production authority; retain until ownership is resolved |

## Programming-file rules

### KEEP

Keep code when it is:

- imported by canonical runtime;
- exercised by current tests;
- referenced by active build/deployment;
- required by an active capability;
- a reusable adapter with a defined contract;
- required for security, privacy, migration or recovery;
- active research that has a documented owner and boundary.

### MODIFY / REFACTOR

Modify code when it is useful but:

- duplicates a canonical implementation;
- violates the capability boundary;
- contains hard-coded environment assumptions;
- couples one interface to another;
- has unsafe implicit transport selection;
- claims stronger privacy/security guarantees than it actually provides;
- has no explicit degraded/failure state.

### ARCHIVE

Archive code only when all are true:

1. no canonical runtime imports it;
2. no active build/deployment depends on it;
3. no required test depends on it;
4. a replacement exists or the capability is intentionally deferred;
5. historical/research value warrants retention;
6. archive metadata records why it was archived.

## Specific architectural caution

The V3 architecture documentation contains ambitious claims such as automatic transport switching, strict zero-retention behavior, air-gapped model operation and legal escalation generation. These must be treated as **design claims requiring implementation evidence**, not as automatically true properties of the product. The V3 architecture index itself describes Android/iOS/WASM targets and decentralized/AI modules, but this is not sufficient to establish production readiness. fileciteturn854file0L2-L2

In particular:

- transport selection must be explicit and policy-controlled;
- privacy guarantees must distinguish transient processing, stored case state and telemetry;
- AI-generated legal text must remain subject to source grounding and user review;
- blockchain/decentralized components must not become universal availability dependencies;
- emergency workflows need independently tested degraded paths.

## Documentation consolidation target

The desired hierarchy is:

```text
NORTH STAR
   ↓
ECOSYSTEM CHARTER
   ↓
SOURCE OF TRUTH
   ↓
MASTER ARCHITECTURE
   ↓
PRODUCT LANDSCAPE
   ↓
ROADMAP
   ↓
CAPABILITY REGISTRY + DATA CONTRACTS
   ↓
APP + DAPP BUILD PLAN
   ↓
MASTER TASK CHECKLIST
   ↓
IMPLEMENTATION + TESTS + CI EVIDENCE
   ↓
DATED AUDITS
   ↓
ARCHIVE
```

No lower-level document may silently redefine a higher-level architectural decision.

## App + DApp convergence rules

The first implementation focus is App + DApp. The existing App/DApp build plan already specifies Android/iOS and DApp as independent peers over shared capability contracts, with no blockchain, wallet or AI dependency for ordinary civic workflows. fileciteturn853file0L2-L2

Therefore the codebase must converge toward:

```text
                 Capability Contracts
                  /               \
          Mobile Adapters       DApp Adapter
          /          \              |
      Android       iOS         Browser/Web3
```

rather than:

```text
DApp → Mobile → Web → Telegram
```

or any other interface dependency chain.

## Parallel verification workstream

### Documentation

- [ ] Compare all active architecture documents.
- [ ] Identify duplicates and contradictions.
- [ ] Update README.
- [ ] Update ROADMAP.
- [ ] Update Wiki navigation.
- [ ] Update project map.
- [ ] Rename misleading milestone files only through controlled moves.

### Programming

- [ ] Determine canonical Python runtime entry point.
- [ ] Determine canonical Rust/Dioxus client entry point.
- [ ] Map root ↔ v2 ↔ v3 imports/references.
- [ ] Map build/deployment ownership.
- [ ] Map App/DApp code actually present.
- [ ] Map unused/duplicate modules.
- [ ] Map storage ownership.
- [ ] Map document-generator ownership.
- [ ] Map AI provider/model ownership.
- [ ] Map decentralized adapter ownership.

### Verification

- [ ] Run complete Python tests.
- [ ] Run Rust tests for canonical client/protocol code.
- [ ] Run build checks for App target(s).
- [ ] Run DApp/WebAssembly build checks.
- [ ] Verify failure isolation.
- [ ] Verify privacy defaults.
- [ ] Verify wallet/no-wallet boundary.
- [ ] Verify AI/manual fallback.
- [ ] Record evidence in the milestone status register.

## Archive batch policy

Do **not** create a large archive commit merely because many files look old.

Archive in small, reviewable batches:

1. duplicate documentation;
2. superseded planning notes;
3. proven-unused scripts;
4. proven-unused code;
5. old implementation generations after migration evidence.

Each batch should have:

- a precise commit message;
- a manifest of moved items;
- reason for archival;
- replacement path where applicable;
- test evidence.

## Immediate next action

**Do not archive `janavani_v2` or `janavani_v3` yet.**

First complete the App/DApp runtime and dependency map. Then archive or migrate specific components based on evidence.

This keeps the repository safe while still aggressively reducing architectural duplication.
