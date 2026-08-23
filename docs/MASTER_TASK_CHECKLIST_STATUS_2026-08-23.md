# JANAVANI — MASTER TASK CHECKLIST STATUS REGISTER

**Date:** 23 August 2026  
**Purpose:** Immutable progress record for the Master Task Checklist. This file records verified status changes without replacing the canonical checklist.  
**Rule:** The master checklist remains the authoritative task inventory; this register records what has been completed/verified and the evidence supporting the status.

---

# 1. VERIFIED COMPLETIONS / STATUS CHANGES

### Architecture & governance

- [x] 1.1 `docs/JANAVANI_MASTER_ARCHITECTURE.md` exists.
- [x] 1.2 Capability-first architecture locked.
- [x] 1.3 Independent-channel principle locked.
- [x] 1.4 AI/non-AI independence principle locked.
- [x] 1.5 Mesh is treated as a current SOS capability.
- [x] 1.6 Satellite is treated as a current SOS capability.
- [x] 1.7 Archive-over-delete principle locked.

### Capability registry

- [x] 3.1–3.16 Capability registry created and committed as `docs/CAPABILITY_REGISTRY.md`.
- Evidence commit: `b793c24eaa632e74fbecccd8ce6bcad3f6a8f8e1`

### Core data contracts

- [x] 4.1–4.18 Core data-contract layer created and committed as `docs/DATA_CONTRACTS.md`.
- Evidence commit: `8a856573a73169f31ab56502f045297f8d12175d`

### Repository reconciliation — static

- [x] 2.1 Static repository/tree inventory performed.
- [x] 2.4 Static database/storage inventory performed.
- [x] 2.6 Static decentralised-component inventory performed.
- [x] 2.9 Static implementation-vs-architecture comparison performed.
- [x] 2.10 Preliminary duplicate/obsolete implementation identification performed.
- [x] 2.12 Architecture-gap report created.
- Evidence file: `docs/REPOSITORY_RECONCILIATION_AUDIT_2026-08-23.md`
- Evidence commit: `a4036f669fe63bb821ba8b632bd17e0564c40045`

### Repository reconciliation — runtime/import/deployment mapping

- [x] M2-A static runtime/import/dependency map substantially completed.
- Evidence file: `docs/RUNTIME_IMPORT_DEPENDENCY_MAP_2026-08-23.md`
- Evidence commit: `4aebc04409399b8e8dc5843e58946d723407d32a`
- [x] Candidate executable entry points identified.
- [x] Telegram import chain mapped.
- [x] Directory/search dependency mapped.
- [x] Document dependency mapped.
- [x] AI dependency paths mapped.
- [x] Storage dependency families identified.
- [x] SOS dependency path identified.
- [x] Render/entrypoint/Docker deployment paths identified.
- [x] Major runtime/deployment conflicts recorded.

### M2-B — Capability → Repository → Test → Deployment static map

- [x] Capability-to-repository evidence mapped.
- [x] Capability-to-test evidence mapped.
- [x] Capability-to-deployment evidence mapped where repository evidence exists.
- [x] Capability status discipline established: PRESENT / PARTIAL / POC / DESIGN / UNVERIFIED / BLOCKED / VERIFIED.
- Evidence file: `docs/CAPABILITY_REPOSITORY_TEST_DEPLOYMENT_MAP_2026-08-23.md`.
- **Important:** this is static evidence mapping, not runtime verification.

### M2-D — Storage ownership reconciliation

- [x] Local CSV/JSONL persistence surfaces identified.
- [x] Repository/storage modules identified.
- [x] Redis transient-storage surfaces identified.
- [x] Supabase/PostgreSQL intended durable-storage path identified.
- [x] V2/V3 decentralised/experimental storage surfaces identified.
- [x] Canonical ownership target defined for major domain objects.
- [x] Storage conflicts recorded: JSONL vs repositories, CSV vs office repository, durable ratings vs Redis aggregates, Supabase vs local files.
- [x] Migration and archive safety rules defined.
- Evidence file: `docs/STORAGE_OWNERSHIP_MAP_2026-08-23.md`.
- **Important:** ownership design is complete; runtime migration has NOT started.

### M3-D — Canonical API assembly control

- [x] M3-D.1 pre-refactor freeze completed; baseline `src/web/app.py` SHA recorded.
- [x] M3-D.2 feedback route facade extracted without changing the existing implementation or public path.
- [x] M3-D.3 canonical FastAPI candidate isolated as `src.web.canonical_app:app` without modifying legacy `src/web/app.py`.
- [x] M3-D.4 canonical application verification test artifact created in `tests/test_canonical_app.py`.
- **Important:** M3-D.4 test execution is NOT yet verified; the test artifact is not evidence of a passing runtime result.
- Evidence: `docs/M3_D1_PRE_REFACTOR_FREEZE_2026-08-23.md`, `docs/M3_D2_FEEDBACK_EXTRACTION_RESULT_2026-08-23.md`, `docs/M3_D3_CANONICAL_APP_ISOLATION_RESULT_2026-08-23.md`, `docs/M3_D4_CANONICAL_APP_VERIFICATION_2026-08-23.md`.

> Static/runtime-configuration mapping does **not** mark live runtime, integration, security or deployment functionality complete. Those require actual execution evidence.

---

# 2. MASTER TASKS CURRENTLY IN PROGRESS

## 1. Master architecture & system governance

**Status: IN PROGRESS**

Remaining:

- [ ] 1.10 Formal permission/consent contracts.
- [ ] 1.11 Transport abstraction contracts.
- [ ] 1.12 Failure/dependency matrix.
- [ ] 1.13 System-wide threat model.
- [ ] 1.14 System-wide test strategy.

## 2. Repository baseline & architecture reconciliation

**Status: IN PROGRESS — STATIC MAPPING SUBSTANTIALLY COMPLETE; LIVE EXECUTION OPEN**

Remaining:

- [ ] 2.2 Live runtime entry-point verification.
- [ ] 2.3 Runtime API/service execution inventory.
- [ ] 2.5 Runtime AI integration verification.
- [ ] 2.7 Runtime SOS execution verification.
- [ ] 2.8 Test/CI execution evidence inventory.
- [ ] 2.11 Archive obsolete material only after dependency/replacement/runtime verification.

## 3. Capability registry

**Status: COMPLETE AS DESIGN REGISTER; STATIC IMPLEMENTATION MAPPING COMPLETE; RUNTIME VERIFICATION PENDING**

Evidence: `CAPABILITY_REGISTRY.md` + `CAPABILITY_REPOSITORY_TEST_DEPLOYMENT_MAP_2026-08-23.md`.

## 4. Core data contracts

**Status: COMPLETE AS DESIGN REGISTER; STORAGE OWNERSHIP MAPPED; IMPLEMENTATION MIGRATION PENDING**

Evidence: `DATA_CONTRACTS.md` + `STORAGE_OWNERSHIP_MAP_2026-08-23.md`.

## M3-A — Actual CI/test execution evidence

**Status: NOT VERIFIED — OPEN**

GitHub issue: **#18 — M3-A: Obtain actual CI/test execution evidence**.

Required evidence remains:

- actual Python pytest result;
- actual Python compile result;
- actual Rust/Dioxus result where applicable;
- GitHub Actions execution status;
- failure classification if any;
- timestamp and commit SHA.

The workflow definition and test artifacts are configuration/design evidence only.

---

# 3. CURRENT MASTER TASK SNAPSHOT

| Master Task | Status | Evidence |
|---|---|---|
| 1 Architecture & Governance | IN PROGRESS | Master architecture + capability/data contracts |
| 2 Repository Reconciliation | IN PROGRESS — STATIC MAPPING COMPLETE | Reconciliation + runtime/import + capability + storage maps |
| 3 Capability Registry | COMPLETE — DESIGN + STATIC MAPPING | `CAPABILITY_REGISTRY.md`, capability map |
| 4 Data Contracts | COMPLETE — DESIGN + STORAGE OWNERSHIP MAPPED | `DATA_CONTRACTS.md`, storage map |
| 5 Identity/Access | NOT STARTED | — |
| 6 Multilingual/Accessibility | NOT STARTED | — |
| 7 OCR/Vision | NOT STARTED | — |
| 8 RAG/SLM/LLM/Agentic AI | NOT STARTED — POC COMPONENTS EXIST | `api/agent_api.py`, `src/services/legal_agent.py` |
| 9 Civic Document Engine | IN PROGRESS — ARCHITECTURE + PARTIAL IMPLEMENTATION | Document service/generator |
| 10 User Corrections | NOT STARTED | — |
| 11 Accountability | NOT STARTED — PARTIAL MODULES EXIST | Rating/escalation modules |
| 12 Government Schemes | NOT STARTED | — |
| 13 RTI/Evidence | NOT STARTED — PARTIAL DOCUMENT/AI SUPPORT | Existing document/AI components |
| 14 Whistleblower | NOT STARTED | — |
| 15 Expert/Volunteer/NGO | NOT STARTED | — |
| 16 Personal SOS | ARCHITECTURE LOCKED — EXPERIMENTAL PATH EXISTS | `src/services/emergency_sos.py` |
| 17 Mesh SOS | ARCHITECTURE LOCKED — REPOSITORY MATERIAL EXISTS | V2 mesh material |
| 18 Satellite SOS | ARCHITECTURE LOCKED | Data contract + checklist |
| 19 Government Alerts | ARCHITECTURE LOCKED | Data contract + checklist |
| M3-D Canonical API Assembly | IN PROGRESS — STRUCTURAL ISOLATION COMPLETE; RUNTIME VERIFICATION OPEN | M3-D.1–D.4 evidence documents |
| M3-A CI/Test Execution | NOT VERIFIED — OPEN | GitHub issue #18 |

---

# 4. VERIFIED ARCHITECTURAL FINDINGS

### F-01 — Multiple web/API runtimes

Observed:

```text
src/web.py
src/web/app.py
src/web_mvp/main.py
api/agent_api.py
```

**Decision:** No one of these is declared canonical until runtime/deployment verification is completed. The M3-D work now provides a clean FastAPI candidate at `src.web.canonical_app:app`, but it is still a candidate until runtime/deployment verification passes.

### F-02 — Deployment ambiguity

Observed deployment configurations point to different entry points. This remains a P0 convergence item.

### F-03 — `src/web/app.py` structural duplication

Static inspection identified repeated application/router/authentication definitions. M3-D.1 froze the file and M3-D.3 isolated a canonical candidate without deleting the legacy implementation. Further extraction remains gated by actual verification.

### F-04 — Directory remains CSV-backed

The Telegram search path uses `database/offices.csv` through `services/search_directory.py`.

**Decision:** Preserve for now; later migrate to the canonical `GovernmentOffice` contract after storage ownership and runtime are proven.

### F-05 — Document service incomplete against canonical contract

PDF path exists. DOCX remains unimplemented in the observed service. Do not mark full document capability complete.

### F-06 — AI has distinct paths

```text
src/services/legal_agent.py → external AI translation/drafting path
api/agent_api.py → FAISS/RAG POC
```

Keep separate until canonical AI architecture is mapped.

### F-07 — SOS implementation does not equal canonical SOS

`src/services/emergency_sos.py` currently performs Redis cache deletion/token revocation and constructs a Nostr emergency event. This is not sufficient evidence for the canonical trusted-contact + authority-choice + offline + mesh + satellite + acknowledgement SOS capability.

**Decision:** Experimental security/SOS path only until redesigned and verified.

### F-08 — Authentication secret hygiene requires remediation

Static inspection previously identified literal interface-token values in `src/web/app.py`. Treat as a production security blocker if those values are real credentials.

---

# 5. CI / TEST EXECUTION STATUS

The repository's current `.github/workflows/ci.yml` explicitly runs:

```text
python -m compileall src
bash ./run_all_tests.sh
```

and supplies mock AI credentials plus Redis environment variables.

`run_all_tests.sh` currently runs:

```text
python -m pytest tests -v
cargo test -- --nocapture
```

when the root Dioxus package exists. Evidence: `.github/workflows/ci.yml` and `run_all_tests.sh`.

**Current verification result:** The repository interface did not expose a workflow execution result for the latest CI-establishing commit inspected. Therefore no passing CI/test result is claimed. M3-A remains open and is tracked by GitHub issue #18.

---

# 6. REQUIRED STATUS DISCIPLINE

A checkbox in the canonical Master Task Checklist must not be marked `[x]` merely because:

- a file exists;
- a module exists;
- a dependency is installed;
- a roadmap says it exists;
- an architecture document describes it;
- a feature works in a partial/local path.

For engineering completion, record:

```text
IMPLEMENTED
+ TESTED
+ VERIFIED AGAINST ACTUAL FILES
+ SECURITY/PRIVACY REVIEWED WHERE REQUIRED
+ FUNCTIONALLY VERIFIED
+ EVIDENCE COMMIT/PR
```

For design completion, record:

```text
DESIGN DOCUMENT EXISTS
+ CONTRACT DEFINED
+ DEPENDENCIES IDENTIFIED
+ OPEN QUESTIONS RECORDED
```

---

# 7. NEXT MASTER TASKS — LOCKED ORDER

## M3-A — Execute / obtain actual verification evidence

Use the repository's canonical CI/test path and record an actual execution result. Required evidence:

```text
pytest result
Rust/Dioxus result where applicable
compile result
workflow status
failure classification
```

Tracked by GitHub issue #18.

## M3-B — Runtime deployment verification

Trace and verify the actual production entrypoint, web/API process, Telegram process, workers, Redis and durable storage configuration.

## M3-C — Channel integration verification

Verify Telegram, WhatsApp, Messenger, web and other declared ecosystem surfaces against their canonical contracts where implementation exists.

## M3-D — Canonical API assembly verification/extraction

Current subphase: M3-D.4 test artifact exists; execution result is still required. If the canonical-app test passes, continue with controlled agent/SOS extraction. If it fails, remediate only the captured failure.

## M3-E — Evidence record

Record exact command/run, result, timestamp, commit SHA and any blocker in the status register.

---

# 8. ARCHIVE CONTROL

**No archive operation is authorised by this status register.**

Archive requires proof of:

1. no active dependency;
2. no required runtime path;
3. no irreplaceable data;
4. replacement exists where needed;
5. tests pass after removal/deprecation;
6. historical value is preserved;
7. archive location is recorded.

---

# 9. TRACK-LOSS PREVENTION RULE

Every future major Janavani work session must update or reference:

```text
MASTER_TASK_CHECKLIST.md
        +
MASTER_TASK_CHECKLIST_STATUS_<DATE>.md
        +
relevant capability/design document
        +
implementation commit/PR evidence where applicable
```

Before starting a new audit, inspect these records and audit only the unresolved delta. This prevents architecture drift, duplicated work, accidental deletion and hallucinated completion claims.

---

**CURRENT PHASE:** M3-A Actual Verification Evidence Gate / M3-D.4 Canonical App Verification Gate  
**M2-A:** SUBSTANTIALLY COMPLETE  
**M2-B:** STATIC CAPABILITY MAP COMPLETE  
**M2-D:** STORAGE OWNERSHIP DESIGN COMPLETE  
**M3-D.1:** COMPLETE  
**M3-D.2:** STRUCTURAL EXTRACTION PARTIAL / SAFE GATE PASSED  
**M3-D.3:** COMPLETE — STRUCTURAL ISOLATION  
**M3-D.4:** TEST ARTIFACT COMPLETE; EXECUTION NOT VERIFIED  
**M3-A LIVE EXECUTION:** NOT YET VERIFIED  
**DESTRUCTIVE CHANGES:** NONE AUTHORISED  
**NEXT ACTION:** Obtain actual M3-A execution evidence, then continue M3-D only from verified result
