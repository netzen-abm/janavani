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

> Important: static/runtime-configuration mapping does **not** mark live runtime, integration, security or deployment functionality complete. Those require actual execution evidence.

---

# 2. MASTER TASKS CURRENTLY IN PROGRESS

## 1. Master architecture & system governance

**Status: IN PROGRESS**

Remaining:

- [ ] 1.8–1.14 Formal permission/consent, transport, dependency/failure, threat-model and test-strategy documents.

## 2. Repository baseline & architecture reconciliation

**Status: IN PROGRESS — STATIC MAPPING SUBSTANTIALLY COMPLETE**

Remaining verified work:

- [ ] 2.2 Live/import execution verification of entry points.
- [ ] 2.3 Runtime API/service execution inventory.
- [ ] 2.5 Runtime AI integration verification.
- [ ] 2.7 Runtime SOS execution verification.
- [ ] 2.8 Test and CI execution/evidence inventory.
- [ ] 2.9 Runtime comparison against Master Architecture.
- [ ] 2.10 Runtime/dependency confirmation of duplicates and obsolete code.
- [ ] 2.11 Archive candidates only after dependency/replacement verification.

## 3. Capability registry

**Status: COMPLETE AS DESIGN REGISTER; IMPLEMENTATION MAPPING PENDING**

The registry exists, but each capability still requires repository-module, test, deployment and evidence mapping.

## 4. Core data contracts

**Status: COMPLETE AS DESIGN REGISTER; IMPLEMENTATION MAPPING PENDING**

The contracts exist, but database/API schemas must not be changed until storage ownership and runtime mapping are complete.

---

# 3. CURRENT MASTER TASK SNAPSHOT

| Master Task | Status | Evidence |
|---|---|---|
| 1 Architecture & Governance | IN PROGRESS | Master architecture + capability/data contracts |
| 2 Repository Reconciliation | IN PROGRESS — STATIC MAPPING | Reconciliation + runtime/import map |
| 3 Capability Registry | COMPLETE — DESIGN | `CAPABILITY_REGISTRY.md` |
| 4 Data Contracts | COMPLETE — DESIGN | `DATA_CONTRACTS.md` |
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

**Decision:** No one of these is declared canonical until runtime/deployment verification is completed.

### F-02 — Deployment ambiguity

Observed deployment configurations point to different entry points:

```text
render.yaml → src/web.py
entrypoint.sh → src.bot_telegram + src.web
Dockerfile → src.web.app and api.agent_api
```

**Decision:** P0 convergence item.

### F-03 — `src/web/app.py` is structurally duplicated

Static inspection shows repeated application/router/authentication definitions in the same file.

**Decision:** Treat as high-risk convergence target; do not blindly rewrite until actual deployment dependency is verified.

### F-04 — Directory remains CSV-backed

The Telegram search path uses `database/offices.csv` through `services/search_directory.py`.

**Decision:** Preserve for now; later migrate to the canonical `GovernmentOffice` contract after storage ownership is proven.

### F-05 — Document service is incomplete against canonical contract

PDF path exists. DOCX explicitly remains unimplemented in the observed service.

**Decision:** Do not mark full document capability complete.

### F-06 — AI has two distinct paths

Observed:

```text
src/services/legal_agent.py → external AI translation + OpenRouter drafting
api/agent_api.py → FAISS/RAG POC
```

**Decision:** Keep separate until canonical AI architecture is mapped.

### F-07 — SOS implementation does not equal canonical SOS

`src/services/emergency_sos.py` currently performs Redis cache deletion/token revocation and constructs a Nostr emergency event. This is not sufficient evidence for the canonical trusted-contact + authority-choice + offline + mesh + satellite + acknowledgement SOS capability.

**Decision:** Experimental security/SOS path only until redesigned and verified.

### F-08 — Authentication secret hygiene requires remediation

Static inspection of `src/web/app.py` found literal interface-token values.

**Decision:** Treat as a production security blocker if those values are real credentials. Replace with secure secret management before deployment exposure.

---

# 5. REQUIRED STATUS DISCIPLINE

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

# 6. NEXT MASTER TASKS — LOCKED ORDER

### M2-B — Capability → Repository → Test → Deployment Map

For every canonical capability:

```text
Capability ID
→ module(s)
→ data contract(s)
→ entry point(s)
→ channel(s)
→ transport(s)
→ storage
→ test(s)
→ CI
→ deployment evidence
→ security/privacy requirements
→ current status
```

### M2-C — Storage Ownership Map

Map every data source and writer:

```text
database/*.jsonl / CSV
src/storage/*
planning database contracts
V2/V3 storage
external database references
Redis
FAISS / RAG stores
```

No migration until ownership is proven.

### M2-D — Runtime Execution Verification

Run/verify, where the environment permits:

```text
imports
startup
health
Telegram startup
web startup
API startup
Supabase connectivity
Redis connectivity
RAG path
AI provider failure path
SOS failure path
PDF generation
DOCX status
```

Record exact command, result, timestamp and evidence.

---

# 7. ARCHIVE CONTROL

**No archive operation is authorised by this status register.**

Archive requires a separate verified decision showing:

1. no active dependency;
2. no required runtime path;
3. no irreplaceable data;
4. replacement exists where needed;
5. tests pass after removal/deprecation;
6. historical value is preserved;
7. archive location is recorded.

---

# 8. TRACK-LOSS PREVENTION RULE

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

This prevents architecture drift, duplicated work, accidental deletion and hallucinated completion claims.

---

**CURRENT PHASE:** Repository Runtime / Dependency Reconciliation  
**STATIC M2-A:** SUBSTANTIALLY COMPLETE  
**LIVE EXECUTION VERIFICATION:** NOT YET COMPLETE  
**DESTRUCTIVE CHANGES:** NONE AUTHORISED  
**NEXT ACTION:** M2-B Capability → Repository → Test → Deployment Map
