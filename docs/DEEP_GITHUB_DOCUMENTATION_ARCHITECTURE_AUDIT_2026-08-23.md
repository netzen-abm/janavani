# JANAVANI — DEEP GITHUB DOCUMENTATION + ARCHITECTURE AUDIT

**Date:** 23 August 2026  
**Repository:** `netzen-abm/janavani`  
**Branch audited:** `main`  
**Mode:** READ-ONLY ANALYSIS OF APPLICATION ARCHITECTURE + DOCUMENTATION; THIS COMMIT ADDS ONLY THIS AUDIT RECORD  
**Audit type:** DELTA / CROSS-DOCUMENT / CODE-BOUNDARY AUDIT  

---

## 0. WHY THIS AUDIT EXISTS

Several repository audits have already been completed on 23 August 2026. This audit is deliberately **not a repeat** of those inventories.

Already accepted as prior evidence:

- repository/tree inventory;
- static repository reconciliation;
- runtime/import/dependency mapping;
- capability → repository → test → deployment mapping;
- storage ownership reconnaissance/map;
- deployment topology audit;
- runtime entry-point audit;
- canonical API route ownership map;
- canonical FastAPI assembly design;
- feedback route extraction;
- legacy application isolation;
- canonical application route verification.

This audit instead asks a higher-order question:

> **Do the documentation, architecture rules, code boundaries, tests, deployment descriptions and master checklist now describe the same Janavani system?**

The answer is: **not yet.** The repository has a strong architectural direction, but several authoritative documents and executable boundaries have not yet converged.

---

# 1. ECOSYSTEM PERSPECTIVE — CONFIRMED

Janavani is being built as a **full citizen-governance ecosystem**, not as a Telegram bot.

The North Star defines the long-term citizen-government loop:

```text
Citizen Reality
→ Understanding
→ Evidence
→ Correct Authority
→ Citizen Action
→ Government Response
→ Follow-up / Remedy
→ Accountability
→ Public Learning
→ Better Governance
```

The Source of Truth explicitly defines interfaces as independent consumers of a shared Janavani platform and states that Web must not start Telegram as part of normal runtime.

The immediate execution target remains much narrower:

```text
WEB
→ ONE COMPLETE CITIZEN FLOW
→ ISSUE
→ GUIDED WORKFLOW
→ CORRECT OFFICE / FALLBACK
→ COMPLAINT
→ PDF
→ DOWNLOAD
```

This distinction is essential:

**Full ecosystem = destination.**  
**Web MVP = current build target.**  
**Repository reconciliation = prerequisite to safely reaching the MVP.**

---

# 2. PRIOR AUDIT WORK IS NOT TO BE REPEATED

The following are treated as established evidence rather than reopened as duplicate audits:

| Area | Existing evidence | Current interpretation |
|---|---|---|
| Repository tree | `REPOSITORY_RECONCILIATION_AUDIT_2026-08-23.md` | Static mapping substantially complete |
| Runtime/imports | `RUNTIME_IMPORT_DEPENDENCY_MAP_2026-08-23.md` | Candidate paths mapped; execution remains |
| Capability map | `CAPABILITY_REPOSITORY_TEST_DEPLOYMENT_MAP_2026-08-23.md` | Static mapping exists; status text is now stale |
| Storage | `STORAGE_OWNERSHIP_MAP_2026-08-23.md` | Static ownership map complete; migration not started |
| Deployment | `DEPLOYMENT_TOPOLOGY_AUDIT_2026-08-23.md` | Multiple targets remain; runtime evidence required |
| Entry points | `RUNTIME_ENTRYPOINT_AUDIT_2026-08-23.md` | Multiple candidates remain |
| API routes | `CANONICAL_API_ROUTE_OWNERSHIP_MAP_2026-08-23.md` | Domain ownership boundary established |
| Canonical API | `M3_D4_CANONICAL_APP_VERIFICATION_2026-08-23.md` | Structural verification passed locally |
| Legacy isolation | `M3_D3_CANONICAL_APP_ISOLATION_RESULT_2026-08-23.md` | Canonical app does not import legacy `src.web.app` |

Therefore the next work should be **convergence and runtime verification**, not another broad inventory.

---

# 3. DOCUMENTATION AUTHORITY AUDIT

## 3.1 The intended hierarchy is correct

The repository establishes the following hierarchy:

```text
NORTH STAR
↓
SOURCE OF TRUTH
↓
MASTER ARCHITECTURE
↓
PRODUCT LANDSCAPE
↓
ROADMAP
↓
PROJECT MAP
↓
MASTER TASK CHECKLIST
↓
IMPLEMENTATION
↓
TEST / DEPLOYMENT EVIDENCE
```

This is the correct conceptual structure.

## 3.2 The hierarchy is not yet synchronised

The problem is not missing documentation. The problem is **state divergence between documents written at different phases**.

Examples found in the current `main` branch:

### A. Master checklist is behind the status register

`MASTER_TASK_CHECKLIST.md` still shows:

- capability registry creation unchecked;
- data contracts unchecked;
- several repository reconciliation tasks unchecked.

But `MASTER_TASK_CHECKLIST_STATUS_2026-08-23.md` records those as verified completions and cites evidence commits.

**Finding:** The canonical task inventory and its status register disagree.

**Impact:** High. This creates false work-in-progress signals and can cause repeated audits or accidental re-execution of completed work.

**Required action:** Reconcile the checklist with the evidence register before starting another major workstream.

---

### B. Capability map is stale relative to M2-D/M3-D

`CAPABILITY_REPOSITORY_TEST_DEPLOYMENT_MAP_2026-08-23.md` still describes M2-D storage ownership as the next phase, while `STORAGE_OWNERSHIP_MAP_2026-08-23.md` already records M2-D static reconciliation as complete and the repository has progressed through M3-D canonical API work.

**Finding:** The capability map is historically useful but no longer an accurate current-status dashboard.

**Required action:** Preserve its historical mapping but update its phase/status section to point to the current M3 state.

---

### C. Source of Truth predates the canonical API assembly

`SOURCE_OF_TRUTH.md` identifies `src/web/app.py` as the current Web implementation and describes `src/web.py` and `src/main.py` as older/transition files.

A newer canonical API assembly now exists at:

```text
src/web/canonical_app.py
```

and the M3-D work explicitly established this as the canonical FastAPI assembly boundary.

**Finding:** The Source of Truth is architecturally correct but now requires a bounded amendment so that it distinguishes:

```text
Web interface/runtime
        ≠
Canonical API assembly boundary
```

This must not become a reason to declare `src/web/app.py` obsolete. Runtime/deployment verification is still required.

---

### D. Historical documentation is valuable but insufficiently classified

The repository contains root architecture indexes, `docs/`, `planning/`, `janavani_v2/`, `janavani_v3/`, `archive/` and legacy documentation.

The current documentation policy says documents should be classified as:

```text
CANONICAL
CURRENT SUPPORTING
EXPERIMENTAL
HISTORICAL
SUPERSEDED
ARCHIVE CANDIDATE
```

The policy itself is sound, but the classification is not yet consistently applied to every major document.

**Required action:** Build a documentation state register rather than deleting older documents.

---

# 4. ARCHITECTURE-TO-CODE CONSISTENCY AUDIT

## 4.1 Canonical API boundary — GOOD

`src/web/canonical_app.py` is a clean assembly boundary. It imports domain routers directly and deliberately avoids importing the historical `src.web.app` module.

Current structural route tests passed locally:

```text
4 passed, 1 warning
```

This is a meaningful convergence milestone.

**Status:** STRUCTURALLY VERIFIED; PRODUCTION RUNTIME NOT YET VERIFIED.

---

## 4.2 `src/web.py` violates the current deployment principle

The Source of Truth explicitly says:

```text
Web must NOT start Telegram.
```

However, `src/web.py` currently contains a `subprocess.Popen(...)` invocation that starts:

```text
src/bot_telegram.py
```

before starting its Flask server.

**Finding F-NEW-01 — Interface coupling remains in a historical runtime.**

This is not merely cosmetic. It directly conflicts with the locked independent-runtime principle.

**Decision:** Do not delete `src/web.py` yet. First establish whether any deployment still uses it. If it is active, replace the coupled deployment topology with independent runtimes. If it is historical, classify it accordingly.

**Priority:** P0 runtime/deployment verification.

---

## 4.3 `src/main.py` remains a stale executable boundary

Current `src/main.py` imports:

```text
from tools.search_directory import search_office
from tools.rate_office import save_rating
from tools.generate_pdf import generate_complaint_pdf
```

The current root source tree does not define the `tools/` package corresponding to these imports. The repository's open PR #17 specifically identifies this class of failure as a prior startup regression.

**Finding F-NEW-02 — Stale executable imports remain on main.**

This is stronger evidence than simply saying “multiple entry points exist”: one candidate entry point is structurally disconnected from the current source layout.

**Decision:** Treat `src/main.py` as a legacy/transition candidate until PR/runtime verification establishes whether it has any active consumer.

**Priority:** P1 after canonical runtime verification.

---

## 4.4 Root Flask and canonical FastAPI are different architectural generations

The repository currently contains:

```text
src/web.py              Flask historical/simple runtime
src/web/app.py          large historical/transition FastAPI application
src/web/canonical_app.py new canonical FastAPI assembly
```

The correct approach is not to choose one by filename.

The correct sequence is:

```text
deployment evidence
→ import execution
→ route inventory
→ dependency verification
→ functional smoke test
→ canonical runtime decision
→ bounded migration
→ deprecation/archive
```

**Finding:** Canonical API assembly is now clearer, but canonical production runtime is still not proven.

---

# 5. DOMAIN BOUNDARY AUDIT

## 5.1 Shared platform layers are reasonably well separated

The root architecture contains distinct:

```text
conversation
workflow
engine
 domain
services
documents
storage
models
web/adapters
```

This is a strong foundation for a multi-interface ecosystem.

## 5.2 Legacy service paths still bypass intended abstractions

The storage audit already established direct JSONL/CSV writes and reads in services.

The important architectural conclusion is now stronger:

```text
Capability
→ Service/domain logic
→ Repository/data-access boundary
→ Canonical durable storage
```

is the target, while some current paths still behave like:

```text
Capability
→ service
→ filesystem directly
```

**Finding F-NEW-03 — Repository abstraction is not yet universal.**

Do not migrate storage yet. First map every reader/writer, then introduce repository ownership one domain at a time.

---

# 6. TEST ARCHITECTURE AUDIT

The repository has substantial test material, but the test architecture has three distinct classes:

```text
A. Root tests
B. V2 tests
C. V3 tests
```

There are also test placeholders and orchestration scripts.

The important distinction is:

```text
Test file exists
≠
Test passes
≠
CI executes test
≠
Production runtime verified
```

The canonical API test has now provided actual local execution evidence, which is better than static test inventory alone.

**Finding F-NEW-04 — Evidence maturity is uneven across generations.**

### Required test evidence model

Every important capability should eventually have:

```text
UNIT
↓
INTEGRATION
↓
ENTRY-POINT SMOKE
↓
CI
↓
DEPLOYMENT SMOKE
↓
USER FLOW
```

Only the applicable layers need to exist for every capability, but the evidence level must be explicit.

---

# 7. CI / WORKFLOW ARCHITECTURE AUDIT

The repository contains a large number of GitHub Actions workflows, including workflows for:

- Python build/test/package variants;
- Docker;
- security;
- dependency review;
- AI compliance;
- decentralized/Freenet verification;
- deployment platforms;
- generic template workflows such as Django/Jekyll/OpenShift/Octopus-related workflows.

**Finding F-NEW-05 — Workflow sprawl creates governance risk.**

This does not mean the workflows should be deleted.

The correct next action is to classify each workflow:

```text
CANONICAL CI
SECURITY GATE
RELEASE/DEPLOYMENT
EXPERIMENTAL
V2/V3
GENERIC TEMPLATE / UNUSED
HISTORICAL
```

Then define which workflows are required gates for `main`.

**Priority:** P1, after runtime convergence.

---

# 8. PULL REQUEST / BRANCH STATE AUDIT

Open PR #17 remains unmerged and addresses several known runtime/CI regressions, including:

- stale `tools` imports;
- Messenger/WhatsApp service alignment;
- Docker Compose consolidation;
- Python module path/startup alignment.

Therefore PR #17 is **candidate evidence**, not `main` truth.

**Finding F-NEW-06 — Main and proposed repair branch must remain explicitly separated in reasoning.**

No finding from PR #17 should be treated as implemented on `main` until merged and verified.

---

# 9. SECURITY / PRIVACY ARCHITECTURE AUDIT

The architecture consistently states:

- privacy by design;
- minimum data collection;
- user control;
- evidence/provenance separation;
- no false delivery claims;
- AI is not authoritative government truth;
- human approval for consequential actions.

These principles are strong.

However, architecture-level security rules are ahead of verified implementation in several areas.

Existing static audits have already identified possible hard-coded interface token values in historical Web application code.

**Decision:** Keep this as a P0/P1 runtime/security verification item; do not repeat the same static scan unless new code changes occur.

---

# 10. FULL ECOSYSTEM BUILD STRATEGY — RECONFIRMED

The repository should now be understood as five concentric layers:

```text
LAYER 1 — NORTH STAR
Citizen capability / accountable governance

LAYER 2 — SHARED PLATFORM
Domain + workflow + services + documents + storage + evidence

LAYER 3 — CANONICAL API
Stable capability boundary for independent interfaces

LAYER 4 — CHANNELS
Web / Telegram / WhatsApp / Messenger / Android / iOS / API / DApp

LAYER 5 — SPECIALISED TRANSPORTS
Internet / local / mesh / satellite / decentralised adapters
```

The current work is primarily moving the repository from an older mixed-generation Layer 2/3 state toward a stable Layer 3 boundary.

That is why the canonical API work is important even though the visible product target is the Web MVP.

---

# 11. WHAT THIS MEANS FOR THE WEB MVP

We should **not** immediately build a new Web application from scratch.

The correct sequence is:

```text
1. Finish canonical runtime/deployment verification.
2. Stabilise canonical API/domain boundaries.
3. Identify which existing shared services are safe to consume.
4. Build Web UI against those boundaries.
5. Complete one citizen complaint flow.
6. Verify PDF generation/download.
7. Add verification/fallback behavior.
8. Harden security/privacy.
9. Only then expand to the broader ecosystem.
```

This preserves the working Telegram capability while preventing the Web interface from becoming another isolated implementation.

---

# 12. NEW MASTER-CHECKLIST ALIGNMENT REQUIRED

The master checklist should be treated as the execution controller.

Immediate reconciliation required:

### M1 — Architecture & Governance

- Mark capability registry creation complete where evidence exists.
- Mark data contracts complete where evidence exists.
- Keep permission/transport/failure/threat/test-strategy documents in progress until created and reviewed.

### M2 — Repository Reconciliation

Static tasks with evidence should be marked complete.

Runtime tasks must remain open until actual execution evidence exists.

### M2-B / M2-C

Capability → repository → test → deployment static mapping exists.

### M2-D

Storage ownership static mapping exists.

### M3-D

Canonical API assembly and structural verification are now evidenced.

### Next execution gate

```text
M3-A / runtime verification
        ↓
canonical runtime decision
        ↓
storage runtime verification
        ↓
deployment verification
        ↓
Web MVP implementation
```

---

# 13. NO-DELETION / NO-BIG-REWRITE DECISION

This audit authorises **no deletion**.

It also does not authorise:

- replacing `src/web/app.py` wholesale;
- deleting V2/V3;
- deleting decentralised components;
- migrating storage immediately;
- rewriting Telegram;
- replacing the architecture with a new framework;
- declaring production readiness.

The repository is too valuable and the ecosystem too broad for a destructive convergence strategy.

---

# 14. CURRENT STATUS AFTER THIS AUDIT

| Area | Status |
|---|---|
| Full ecosystem vision | CONFIRMED |
| North Star | CANONICAL |
| Source of Truth | CANONICAL, NEEDS BOUNDED UPDATE FOR M3 API BOUNDARY |
| Master architecture | CANONICAL DESIGN |
| Capability registry | DESIGN COMPLETE |
| Data contracts | DESIGN COMPLETE |
| Static repository reconciliation | COMPLETE |
| Static storage ownership | COMPLETE |
| Static capability mapping | COMPLETE |
| Canonical API assembly | STRUCTURALLY VERIFIED |
| Canonical production runtime | NOT VERIFIED |
| Deployment convergence | NOT COMPLETE |
| Storage runtime ownership | NOT VERIFIED |
| CI/test evidence convergence | NOT COMPLETE |
| Web MVP | NEXT BUILD TARGET |
| Telegram | WORKING/FROZEN; avoid unnecessary changes |
| V2/V3 | RETAIN / EXPERIMENTAL-PARALLEL until ownership proven |
| Archive/deletion | NONE AUTHORISED |

---

# 15. NEXT TWO EXECUTION STEPS

## NEXT STEP 1 — MASTER CHECKLIST RECONCILIATION

Synchronise `MASTER_TASK_CHECKLIST.md`, `MASTER_TASK_CHECKLIST_STATUS_2026-08-23.md` and the latest M2/M3 evidence so completed static work is not repeated.

## NEXT STEP 2 — M3 RUNTIME VERIFICATION

Execute and record actual evidence for:

```text
canonical API import/startup
legacy Web runtime import
src/web.py import/startup
src/main.py import viability
Telegram startup boundary
Redis availability
Supabase availability/configuration
document generation
AI failure/fallback path
SOS experimental path
Docker/entrypoint path
```

Only after this evidence is captured should we make the canonical production runtime decision.

---

# 16. FINAL CONCLUSION

Janavani is not suffering from a lack of architecture.

It is suffering from **architecture-to-implementation-to-documentation convergence debt** caused by several generations of development existing simultaneously.

The solution is therefore not another redesign.

The solution is:

```text
REMEMBER THE WHOLE ECOSYSTEM
        ↓
KEEP THE NORTH STAR
        ↓
KEEP THE WORKING TELEGRAM CORE
        ↓
CONVERGE THE API BOUNDARY
        ↓
VERIFY RUNTIME / DEPLOYMENT
        ↓
NORMALISE STORAGE OWNERSHIP
        ↓
BUILD WEB MVP ON SHARED CAPABILITIES
        ↓
EXPAND CAPABILITY BY CAPABILITY
        ↓
VERIFY EACH CAPABILITY
        ↓
GROW INTO THE FULL JANAVANI ECOSYSTEM
```

**This is the governing interpretation for the next phase.**

---

**END OF AUDIT**
