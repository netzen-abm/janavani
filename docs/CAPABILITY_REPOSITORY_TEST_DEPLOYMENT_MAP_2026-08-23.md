# JANAVANI — CAPABILITY → REPOSITORY → TEST → DEPLOYMENT MAP

**Date:** 23 August 2026  
**Mode:** READ-ONLY RECONCILIATION  
**Repository:** `netzen-abm/janavani`  
**Purpose:** Map canonical ecosystem capabilities to observable repository modules, tests, CI/deployment evidence and verification state.

> **Important:** A source file or test file proves that implementation/test material exists. It does **not** prove production completeness. `VERIFIED` is reserved for evidence of successful execution/integration; this document therefore uses `PRESENT`, `PARTIAL`, `POC`, `DESIGN`, and `UNVERIFIED` where appropriate.

---

# 1. STATUS LEGEND

| Status | Meaning |
|---|---|
| PRESENT | Relevant implementation exists in repository |
| PARTIAL | Some implementation exists but canonical contract is incomplete |
| POC | Experimental/proof-of-concept path |
| DESIGN | Capability exists in architecture/planning but no verified implementation path |
| UNVERIFIED | Code/config exists but runtime result has not been established |
| BLOCKED | Known issue prevents treating capability as production-ready |
| VERIFIED | Execution/integration evidence exists and is recorded |

---

# 2. CAPABILITY MAP

## C-01 — Citizen Civic Complaint

**Repository evidence**

```text
src/bot_telegram.py
src/commands/complaint.py
src/conversation/
src/services/document_service.py
src/documents/complaint_builder.py
```

**Tests**

- `tests/test_document_generation.py`
- `tests/test_documents.py` exists but is empty
- broader system orchestration in `run_all_tests.sh`

**Deployment evidence**

- Telegram adapter exists
- Render/entrypoint deploy Telegram alongside web

**Status:** PARTIAL / UNVERIFIED

**Gap:** Full canonical complaint lifecycle, document contract, submission tracking, evidence provenance and multi-channel consistency remain unverified.

---

## C-02 — Government Office Search

**Repository evidence**

```text
src/commands/search.py
src/services/search_directory.py
database/offices.csv
```

**Tests**

No dedicated `test_office_search` result was identified in the inspected root test inventory.

**Status:** PRESENT / LEGACY / UNVERIFIED

**Gap:** CSV schema is narrower than canonical `GovernmentOffice`; address verification/correction lifecycle is not yet mapped.

---

## C-03 — Office/Officer Rating

**Repository evidence**

```text
src/commands/rate.py
src/services/rate_office.py
database/ratings.jsonl
tests/test_accountability_feedback.py
```

**Status:** PRESENT / PARTIAL

**Gap:** Canonical evidence-aware rating model, anti-abuse controls, public display permissions and full government-demand disclosure remain to be verified.

---

## C-04 — Government-Ready Document Generation

**Repository evidence**

```text
src/services/document_service.py
src/documents/complaint_builder.py
src/documents/generate_pdf.py
src/documents/pdf_generator.py
```

**Tests**

- `tests/test_document_generation.py`

**Status:** PARTIAL / BLOCKED FOR FULL CONTRACT

**Known gap:** PDF path exists; document service explicitly reports DOCX as not implemented. Full To/CC postal address + email, user verification, submission state and archive lifecycle are not yet established.

---

## C-05 — Legal/Policy AI Assistance

**Repository evidence**

```text
src/services/legal_agent.py
src/legal_brain.py
```

**Tests**

- `tests/test_ai_agent_components.py` appears in the system test orchestrator
- `tests/test_local_slm_prompts.py`

**Status:** PRESENT / UNVERIFIED

**Gap:** Canonical provider abstraction, provenance, human approval, citation enforcement, privacy boundaries and offline fallback require formal mapping.

---

## C-06 — RAG Knowledge System

**Repository evidence**

```text
api/agent_api.py
services/rag_agent.py
services/agent_runner.py
FAISS path in agent API
```

**Tests:** RAG-specific execution not yet proven from inspected CI.

**Status:** POC

**Decision:** Keep isolated until canonical RAG contracts are established.

---

## C-07 — Local SLM / Offline AI

**Repository evidence**

```text
src/local_slm/
tests/test_local_slm_prompts.py
```

**Status:** PRESENT / UNVERIFIED

**Gap:** Device capability matrix, model packaging, offline storage, language coverage and deterministic fallback need evidence.

---

## C-08 — Constitutional / Legislative Analysis

**Repository evidence**

```text
src/web/app.py
src/web/constitutional_router.py
src/web/legislative_router.py
src/web_mvp/main.py
```

**Tests**

- `tests/test_constitutional_compliance.py`

**Status:** PRESENT / UNVERIFIED

---

## C-09 — Land / Geospatial Services

**Repository evidence**

```text
src/web/land_router.py
```

**Tests**

- `tests/test_geodetic_mapping.py`

**Status:** PRESENT / UNVERIFIED

---

## C-10 — Personal SOS

**Repository evidence**

```text
src/services/emergency_sos.py
src/web/app.py
```

**Tests**

- `tests/test_emergency_lockdown.py`

**Status:** EXPERIMENTAL / NOT CANONICAL

**Gap:** Current emergency engine is oriented around lockdown/cache handling and Nostr event construction rather than the full user-controlled SOS contract.

---

## C-11 — Mesh SOS

**Repository evidence**

- `janavani_v2/` mesh architecture/install material
- decentralised transport material in repository

**Tests:** no verified end-to-end mesh SOS delivery evidence in inspected root test inventory.

**Status:** PRESENT IN EXPERIMENTAL ARCHITECTURE / UNVERIFIED E2E

---

## C-12 — Satellite SOS

**Repository evidence:** architectural requirement exists; no verified production satellite adapter identified in this audit.

**Status:** DESIGN

---

## C-13 — Government Emergency Alerts

**Repository evidence:** capability/data-contract architecture only in current reconciliation.

**Status:** DESIGN

---

## C-14 — Whistleblower Protection

**Repository evidence:** canonical capability/data-contract architecture; no verified secure production workflow identified in current repository mapping.

**Status:** DESIGN / HIGH-RISK FUTURE IMPLEMENTATION

**Required before implementation:** threat model, anonymity model, metadata minimisation, secure evidence handling, access controls, audit boundaries and legal-process design.

---

## C-15 — Financial Transparency / Contributions

**Repository evidence:** canonical data-contract design; no verified production finance module identified in current mapping.

**Status:** DESIGN

**Required:** contributor-display preferences, full-demand disclosure model, immutable audit/provenance, correction process, archive lifecycle and regulatory review.

---

## C-16 — Expert / Volunteer / NGO Participation

**Repository evidence:** some volunteer/participant architecture exists in repository planning, but no complete canonical `ContributorProfile` runtime path has been verified.

**Status:** PARTIAL / DESIGN

---

## C-17 — Address Correction / Community Verification

**Repository evidence:** directory service and broader architecture exist; dedicated canonical correction workflow not verified.

**Status:** DESIGN / PARTIAL FOUNDATION

---

## C-18 — Evidence & Provenance

**Repository evidence**

- document/evidence infrastructure
- security anchor tests
- decentralised protocol material

**Tests**

- `tests/test_security_anchors.py`
- `tests/test_production_integrity.py`

**Status:** PARTIAL

**Canonical direction:** evidence must remain usable without blockchain; blockchain is an optional integrity/provenance anchor.

---

## C-19 — Blockchain / Decentralised Anchoring

**Repository evidence**

- root Rust/decentralised dependencies
- V2/V3 decentralised architecture material
- Freenet deployment workflow

**Status:** EXPERIMENTAL / UNVERIFIED

**Rule:** Never make blockchain availability a prerequisite for core evidence storage or citizen service operation.

---

## C-20 — Multi-language / Vernacular Capability

**Repository evidence**

```text
src/services/legal_agent.py
src/web_mvp/main.py
tests/test_vernacular_headers.py
```

**Status:** PARTIAL / UNVERIFIED

**Gap:** The ecosystem requirement is all Indian languages with English default; end-to-end language coverage is not proven by the existence of a vernacular test alone.

---

## C-21 — Telegram Channel

**Repository evidence**

```text
src/bot_telegram.py
src/commands/
src/conversation/
```

**Tests:** system test orchestration references core component tests.

**Deployment:** `entrypoint.sh` starts Telegram process.

**Status:** PRESENT / UNVERIFIED RUNTIME

---

## C-22 — WhatsApp Channel

**Repository evidence:** adapter file exists in root architecture.

**Status:** PRESENT STRUCTURE / UNVERIFIED INTEGRATION

---

## C-23 — Messenger Channel

**Repository evidence:** adapter file exists in root architecture.

**Status:** PRESENT STRUCTURE / UNVERIFIED INTEGRATION

---

## C-24 — Web Client

**Repository evidence**

```text
src/web.py
src/web/app.py
src/web_mvp/
janavani_v3/ Dioxus web target
```

**Status:** MULTIPLE IMPLEMENTATIONS / CONVERGENCE REQUIRED

---

## C-25 — Android / iOS Client

**Repository evidence:** V3 Dioxus workspace targets mobile/desktop/web.

**Status:** ARCHITECTURE/IMPLEMENTATION CANDIDATE / BUILD EVIDENCE REQUIRED

---

## C-26 — Web3 DApp

**Repository evidence:** decentralised Rust/Web3-oriented architecture exists.

**Status:** EXPERIMENTAL / UNVERIFIED

---

# 3. TEST INFRASTRUCTURE FINDING

The repository has a substantial test inventory. Examples include:

```text
test_accountability_feedback.py
test_constitutional_compliance.py
test_document_generation.py
test_emergency_lockdown.py
test_geodetic_mapping.py
test_local_slm_prompts.py
test_production_integrity.py
test_security_anchors.py
test_vernacular_headers.py
```

The root test directory also contains several empty test placeholders such as `test_documents.py`, `test_engine.py` and `test_registry.py`.

**Finding:** Test infrastructure exists, but coverage is uneven and the existence of a test file cannot be equated with passing runtime verification.

---

# 4. CI / DEPLOYMENT EVIDENCE

Root CI currently installs Python 3.12 dependencies and runs:

```text
python -m compileall src
```

It does not, by itself, execute the full pytest suite. fileciteturn339file0

The repository also has additional workflows for AI compliance, dependency review, Docker, Freenet deployment and other infrastructure. fileciteturn338file0

`run_all_tests.sh` contains a much broader intended validation sequence, including pytest suites and Rust/Dioxus tests, but its presence is orchestration evidence rather than proof that all suites currently pass. fileciteturn340file0

---

# 5. CANONICAL EVIDENCE GATE

A capability should only move to **VERIFIED** when all applicable gates are satisfied:

```text
1. Source implementation exists
2. Data contract mapped
3. Entry point mapped
4. Unit/integration tests exist
5. Tests pass
6. CI path verified
7. Deployment target verified
8. Security/privacy review passed
9. Failure/rollback behavior tested
10. User-facing behavior verified
11. Evidence recorded in repository
```

---

# 6. CURRENT PRIORITY MATRIX

| Priority | Capability/area | Reason |
|---|---|---|
| P0 | Web/API runtime convergence | Multiple competing entry points |
| P0 | Secret/authentication hygiene | Potential source-level credential exposure |
| P0 | Storage ownership | Multiple persistence mechanisms |
| P1 | Document contract | PDF exists; DOCX and full address/CC lifecycle incomplete |
| P1 | Government office contract | CSV model narrower than canonical contract |
| P1 | AI architecture | Legal-agent and RAG paths need formal boundary |
| P1 | SOS architecture | Existing emergency engine does not equal canonical SOS |
| P1 | Test execution | CI currently compiles source rather than running complete Python tests |
| P2 | Multi-channel verification | Adapters exist; integrations not proven |
| P2 | Decentralised/Web3 | Experimental architecture should remain optional |
| P2 | Finance/whistleblower | High-risk capabilities require governance/security design first |

---

# 7. MASTER TASK CHECKLIST CROSS-REFERENCE

This map feeds the master checklist but does not replace it.

```text
M1 Architecture & Governance
    ├── M1-A Master Architecture          DONE
    ├── M1-B Capability Registry          DONE
    └── M1-C Data Contracts               DONE

M2 Repository Reconciliation
    ├── M2-A Static repository audit      DONE
    ├── M2-B Runtime/import map           DONE
    ├── M2-C Capability repository map    THIS DOCUMENT / DONE
    └── M2-D Storage ownership map        NEXT

M3 Verification
    ├── M3-A Execute root test suite      NEXT
    ├── M3-B Verify deployment paths      NEXT
    ├── M3-C Verify channel integrations  NEXT
    └── M3-D Record evidence              NEXT

M4 Convergence
    ├── M4-A Canonical runtime decision   PENDING M3
    ├── M4-B Canonical storage decision   PENDING M2-D/M3
    ├── M4-C Migration plans              PENDING
    └── M4-D Deprecation/archive          PENDING
```

---

# 8. ARCHIVE POLICY

No capability mapping in this document authorises deletion.

The lifecycle remains:

```text
KEEP
→ VERIFY
→ CLASSIFY
→ MIGRATE
→ DEPRECATE
→ ARCHIVE
→ DELETE ONLY WHEN PROVEN SAFE
```

---

# 9. NEXT TWO STEPS

## M2-D — Storage Ownership Map

Map every data object and persistence path to one canonical owner:

```text
Citizen
Complaint
Office
Rating
Document
Evidence
Conversation
SOS
Contributor
Finance
Knowledge/RAG
Audit
Archive
```

## M3-A — Execute Verification Suite

Run the actual root test orchestration locally/CI and record:

- pass;
- fail;
- skipped;
- missing dependency;
- external service failure;
- environment failure;
- security failure.

Only then will we classify capabilities as VERIFIED or BLOCKED.

---

# 10. FINAL STATUS

**M2-B Capability → Repository → Test → Deployment map:** COMPLETE FOR STATIC EVIDENCE  
**Runtime verification:** NOT YET COMPLETE  
**Storage ownership map:** NEXT  
**Destructive changes:** NONE AUTHORISED  
**Archive candidates:** NONE AUTHORISED  

**END OF DOCUMENT**
