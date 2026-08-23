# JANAVANI — FULL ECOSYSTEM REPOSITORY AUDIT

**Date:** 23 August 2026  
**Repository:** `netzen-abm/janavani`  
**Branch audited:** `main`  
**Mode:** READ-ONLY RECONNAISSANCE / NO APPLICATION CODE CHANGES  
**Purpose:** Establish a repository-grounded view of what Janavani is, what exists, what is canonical, what is experimental, what is incomplete, and what must happen next.

> This document is an ecosystem audit. It does not promote architectural designs or existing modules to implementation-complete status merely because files exist.

---

## 1. EXECUTIVE CONCLUSION

Janavani is being built as a **full citizen-governance ecosystem**, not as a Telegram bot.

The repository itself supports that conclusion. The canonical Source of Truth explicitly defines Telegram as one interface and describes Web, Android, iOS, WhatsApp, Messenger and API access to a shared Janavani platform. The North Star extends the long-term system from citizen assistance to evidence, action, government response, follow-up, accountability and public learning.

At the same time, the repository is **not yet one clean unified implementation**. It contains multiple generations and experiments:

- root Python platform/application layers;
- Telegram, Web, WhatsApp and Messenger interfaces;
- a canonical FastAPI assembly introduced during M3-D;
- historical/legacy application paths;
- `janavani_v2` and `janavani_v3` workspaces;
- Rust/Dioxus and decentralised protocol work;
- multiple storage generations;
- multiple AI paths;
- multiple deployment descriptions;
- extensive architecture/planning documents.

Therefore the correct engineering objective is:

```text
UNDERSTAND THE WHOLE ECOSYSTEM
        ↓
ESTABLISH CANONICAL BOUNDARIES
        ↓
VERIFY RUNTIME / DEPLOYMENT
        ↓
CONVERGE SAFELY
        ↓
BUILD THE WEB MVP
        ↓
EXPAND THE ECOSYSTEM
```

**Do not perform a broad rewrite or deletion campaign.**

---

## 2. STRATEGIC PERSPECTIVE

### North Star

Janavani's long-term objective is to strengthen the citizen's ability to understand reality, exercise lawful rights, engage government, preserve evidence, obtain remedies, participate in public life and hold public institutions accountable while protecting privacy, dignity, security and citizen control.

The long-term pathway is:

```text
Citizen Reality
    ↓
Understanding
    ↓
Evidence
    ↓
Correct Authority
    ↓
Citizen Action
    ↓
Government Response
    ↓
Follow-up / Remedy
    ↓
Accountability
    ↓
Public Learning
    ↓
Better Governance
```

### Immediate execution target

The long-term ecosystem must not be confused with the immediate build target:

```text
WEB
 ↓
ONE COMPLETE CITIZEN FLOW
 ↓
DESCRIBE ISSUE
 ↓
GUIDED WORKFLOW
 ↓
CORRECT INFORMATION
 ↓
COMPLAINT
 ↓
PDF
 ↓
DOWNLOAD
```

Telegram is frozen except for verified bug, security and shared-core compatibility fixes while the Web MVP is developed.

---

## 3. CANONICAL DOCUMENT HIERARCHY

The repository has established a useful hierarchy:

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

The critical distinction is:

- **North Star:** destination and purpose.
- **Source of Truth:** architectural rules.
- **Product Landscape:** possible capabilities.
- **Roadmap:** sequencing.
- **Master Checklist:** executable work and subtasks.
- **Code:** what actually exists.
- **Tests/deployment evidence:** what is actually verified.

A capability must not be called complete merely because it appears in an architecture document or registry.

---

## 4. REPOSITORY GENERATIONS

### 4.1 Root platform

The root `src/` contains the strongest current Python platform foundation:

- conversation engine and state;
- workflow engine and registry;
- domain models;
- document engine;
- services;
- storage boundary;
- adapters;
- Telegram/Web/WhatsApp/Messenger interfaces;
- AI/legal services;
- constitutional/legislative/land/feedback API routers.

**Classification:** CURRENT CORE / RECONCILE.

### 4.2 `janavani_v2`

V2 is a real parallel workspace containing Python and Rust components, Dioxus material, mesh/protocol work, AI reinforcement, security/air-gapped tests and specialised civic modules.

**Classification:** EXPERIMENTAL / PARALLEL GENERATION UNTIL RUNTIME OWNERSHIP IS PROVEN.

### 4.3 `janavani_v3`

V3 is another parallel workspace with Rust/Dioxus, web/mobile/desktop-oriented configuration, Telegram integration, SOS/legal/privacy material and metrics.

**Classification:** FUTURE/PARALLEL CLIENT-PLATFORM GENERATION UNTIL BUILD AND RUNTIME OWNERSHIP ARE PROVEN.

### 4.4 `archive/`

Legacy modules are already separated into an archive area.

**Classification:** HISTORICAL / RETAIN.

No deletion is authorised merely because code is old.

---

## 5. CURRENT CANONICAL API PROGRESS

M3-D has established a canonical FastAPI assembly at:

`src/web/canonical_app.py`

It currently assembles:

- Feedback
- Legislative
- Constitutional
- Land

and exposes platform liveness/version endpoints.

The canonical assembly deliberately does **not** import the historical `src.web.app` module.

The repository contains tests covering:

- canonical app import;
- liveness;
- version;
- canonical route registration;
- isolation from `src.web.app`.

The latest recorded local verification reported:

```text
4 passed, 1 warning
```

The warning concerns the Starlette/httpx TestClient deprecation path and is not itself a Janavani functional failure.

**Important:** this verifies the canonical assembly boundary, not the entire Janavani runtime.

---

## 6. RUNTIME ENTRY-POINT CONVERGENCE

Observed application candidates include:

```text
src/web.py
src/web/app.py
src/web/canonical_app.py
api/agent_api.py
src/main.py
src/web_mvp/main.py
```

The repository's own deployment audit confirms that multiple runtime targets exist and that one canonical production topology has not yet been fully established.

### Current decision

`src/web/canonical_app.py` is the **canonical API assembly boundary**, but this does not yet prove that every production deployment points to it.

The remaining question is:

```text
Which runtime is actually deployed?
Which deployment should become canonical?
Which historical runtimes are consumers/experiments?
```

This requires runtime and deployment evidence before deletion or replacement.

---

## 7. DEPLOYMENT CONVERGENCE

The repository has historically contained conflicting deployment generations, including Render, Docker, Compose, Railway/Vercel-related deployment activity and multiple application targets.

The current GitHub main commit has reported external deployment failures for Vercel and Railway status contexts.

An open PR #17 attempts to repair runtime imports, Docker Compose structure and startup configuration. It is not merged and must therefore be treated as a candidate change, not current main-branch truth.

### P0 deployment questions

1. What is the canonical production runtime?
2. Which provider is canonical?
3. Which service is Web?
4. Which service is API?
5. Where does Telegram run?
6. Where does Redis run?
7. Where does durable storage run?
8. Which deployment files are active?
9. Which failures are current versus historical?

---

## 8. STORAGE ECOSYSTEM

Observed storage generations include:

```text
database/complaints.jsonl
database/ratings.jsonl
database/offices.csv

src/storage/
    repositories
    cache
    analytics
    Supabase integration

Redis
FAISS / RAG-derived stores
V2/V3 storage-related material
```

### Architectural interpretation

These should not be treated as competing databases without context.

The intended model is:

```text
Durable canonical data
        ↓
PostgreSQL / approved durable store

Ephemeral state
        ↓
Redis

Derived retrieval index
        ↓
FAISS / vector store

Static/bootstrap/reference data
        ↓
Controlled import/seed path

Evidence/files
        ↓
Approved object/document storage
```

The repository has already created a storage ownership map, but runtime writer/reader verification remains necessary.

**No migration or deletion yet.**

---

## 9. AI ECOSYSTEM

AI-related implementation exists in multiple paths:

```text
src/services/ai_service.py
src/services/legal_agent.py
src/legal_brain.py
api/agent_api.py
janavani_v2 AI/reinforcement components
local SLM / Ollama configuration
RAG/FAISS POC material
```

This is evidence of an emerging AI ecosystem, not one final AI architecture.

### Required canonical AI boundary

```text
AI Provider Abstraction
        ↓
Task Router
        ├── deterministic rules
        ├── local SLM
        ├── RAG
        ├── external LLM
        └── agentic tools

Every path must preserve:
source/provenance
confidence
failure fallback
privacy boundary
human approval where consequential
```

AI should assist the platform; it must not become the source of truth for government facts.

---

## 10. CIVIC DOMAIN ECOSYSTEM

The repository contains or references a growing domain set:

### Current/partial implementation evidence

- Complaint/grievance
- Office search
- Document generation
- Feedback/ratings
- Legislative information
- Constitutional/bill workflows
- Land/KML workflow
- Legal intelligence
- Escalation
- Emergency/SOS experimental path

### Design/long-term capability registry

- RTI
- petitions/representations/objections/appeals
- evidence/provenance
- government schemes
- officer/representative accountability
- user corrections
- expert/volunteer/NGO ecosystem
- whistleblower system
- government alerts
- financial transparency
- personal SOS
- mesh SOS
- satellite SOS
- OCR/CV/RAG/SLM/LLM/agents
- decentralised transports and evidence anchoring

The correct status for most of these is **DESIGN / ARCHITECTURE LOCKED / PARTIAL**, not COMPLETE.

---

## 11. INTERFACE ECOSYSTEM

The repository supports the following architectural direction:

```text
                    JANAVANI PLATFORM
                           │
       ┌──────────┬────────┼────────┬──────────┐
       ↓          ↓        ↓        ↓          ↓
      WEB      TELEGRAM  ANDROID   iOS     WHATSAPP
                                      \       /
                                       MESSENGER
```

Additional future access includes API and DApp concepts.

The governing rule is:

> Channels are clients. Janavani capabilities belong to the shared platform.

No channel may become a dependency of another channel.

---

## 12. SECURITY / PRIVACY FINDINGS

The repository's architecture strongly emphasizes:

- privacy by design;
- data minimisation;
- independent channel operation;
- offline honesty;
- no false delivery claims;
- evidence/provenance separation;
- human approval for consequential actions.

However, static audit evidence has identified production-risk areas including hard-coded interface-token values in historical Web application code and unresolved deployment/runtime configuration ambiguity.

These are **P0/P1 verification items**, not reasons to rewrite the platform.

---

## 13. DOCUMENTATION AUDIT RESULT

The repository has unusually extensive documentation. That is an asset, but it creates a second convergence problem: documentation itself exists in generations.

The major documentation families are:

```text
Root architecture/index documents

docs/
    architecture
    source of truth
    north star
    product landscape
    project map
    capability registry
    data contracts
    repository audits
    runtime/deployment maps
    API convergence records

planning/
    product requirements
    MVP constitution
    workflow contracts
    service contracts
    data/database contracts
    privacy architecture
    system domain model

v2/v3 architecture documents
legacy documentation
```

### Documentation rule going forward

Do not delete documentation because it is old.

Instead classify each document:

```text
CANONICAL
CURRENT SUPPORTING
EXPERIMENTAL
HISTORICAL
SUPERSEDED
ARCHIVE CANDIDATE
```

Then cross-link it to the authoritative document that supersedes it.

---

## 14. MASTER CHECKLIST RECONCILIATION

The master checklist remains the task authority, but its current status register lags behind the M3 work now present in GitHub.

Verified newer work includes:

```text
M2-A runtime/import/deployment mapping
M2-B capability → repository → test → deployment mapping
M2-D storage ownership mapping
M3-A CI/test orchestration convergence
M3-B deployment topology audit
M3-B.2 runtime entry-point audit
M3-C canonical API route ownership
M3-D canonical API assembly design
M3-D.2 feedback route boundary
M3-D.3 canonical app isolation
M3-D.4 canonical app verification
```

Therefore the checklist/status register must be kept synchronized before any new broad refactor is started.

### Immediate master-task state

| Master area | Correct interpretation |
|---|---|
| Architecture & governance | IN PROGRESS |
| Repository reconciliation | IN PROGRESS; static mapping substantially complete; runtime verification remains |
| Capability registry | DESIGN COMPLETE; implementation mapping pending |
| Data contracts | DESIGN COMPLETE; implementation/storage mapping pending |
| Identity/access | NOT STARTED |
| Multilingual/accessibility | NOT STARTED |
| OCR/CV | NOT STARTED / DESIGN |
| AI | DESIGN/POC COMPONENTS; canonical architecture pending |
| Document engine | IN PROGRESS / PARTIAL |
| Accountability | PARTIAL MODULES / NOT COMPLETE |
| RTI/evidence | DESIGN / PARTIAL |
| SOS | ARCHITECTURE LOCKED / EXPERIMENTAL IMPLEMENTATION |
| Mesh | ARCHITECTURE LOCKED / RUNTIME UNVERIFIED |
| Satellite | ARCHITECTURE LOCKED / IMPLEMENTATION NOT VERIFIED |
| Government alerts | ARCHITECTURE LOCKED / IMPLEMENTATION NOT VERIFIED |

---

## 15. CRITICAL FINDINGS — PRIORITY ORDER

### P0 — Canonical runtime/deployment still unresolved

Multiple application entry points and deployment descriptions remain.

### P0 — Production deployment status is not green

Current main commit has reported Vercel and Railway failures.

### P0 — Legacy Web application boundary is still high-risk

`src/web/app.py` is large and historically duplicated. The new canonical assembly isolates it, which is safer than direct replacement, but domain-by-domain migration and runtime verification remain.

### P1 — Storage ownership must become executable

The storage map exists, but runtime read/write ownership and durable truth still require evidence.

### P1 — Documentation needs state classification

The repository contains excellent design work but many documents describe different generations or future states.

### P1 — Capability registry must be connected to implementation evidence

A registry entry is not a completed feature.

### P1 — AI needs one canonical boundary

Multiple AI paths exist and must be mapped before integration expands.

### P1 — Deployment configuration requires one canonical production profile

Docker/Compose/provider configuration must converge only after runtime evidence.

---

## 16. WHAT WE ARE NOT DOING

We are **not**:

- reducing Janavani to a Telegram bot;
- deleting V2/V3;
- deleting decentralised work;
- replacing the entire Python architecture;
- migrating storage blindly;
- building every future feature now;
- rewriting `src/web/app.py` wholesale;
- declaring the ecosystem production-ready because architecture documents exist.

---

## 17. WHAT WE ARE DOING

We are establishing a durable engineering chain:

```text
MASTER ARCHITECTURE
        ↓
CAPABILITY REGISTRY
        ↓
DATA CONTRACTS
        ↓
REPOSITORY MAP
        ↓
RUNTIME MAP
        ↓
CANONICAL API BOUNDARY
        ↓
STORAGE OWNERSHIP
        ↓
TEST / CI EVIDENCE
        ↓
DEPLOYMENT EVIDENCE
        ↓
SAFE CONVERGENCE
        ↓
WEB MVP
        ↓
FULL ECOSYSTEM
```

This preserves the original vision while preventing architecture drift.

---

## 18. NEXT EXECUTION ORDER

### Step A — Documentation/state reconciliation

Synchronise the Master Task Checklist and dated status register with M2/M3 evidence.

### Step B — Complete M3 runtime verification

Verify the actual behavior of:

- canonical API;
- legacy Web runtime;
- `src/web.py`;
- `src/main.py`;
- `api/agent_api.py`;
- Web MVP;
- deployment entry points.

### Step C — Capability implementation mapping

For each capability:

```text
Capability ID
→ module
→ contract
→ entry point
→ channel
→ transport
→ storage
→ test
→ CI
→ deployment
→ security/privacy
→ evidence
→ status
```

### Step D — Storage runtime verification

Verify every durable writer, reader, cache writer, seed path and migration path before any database change.

### Step E — Web MVP completion

Only after the canonical boundaries are verified, complete the one full Web citizen journey.

### Step F — Reliability/security gate

Run the full test and deployment validation suite before expanding major capabilities.

### Step G — Ecosystem expansion

Then progressively activate:

```text
Evidence
→ Tracking
→ Follow-up
→ Escalation
→ AI
→ Multilingual
→ Accountability
→ Schemes
→ RTI
→ Expert/NGO network
→ SOS
→ Mesh/Satellite
→ broader governance intelligence
→ additional channels
```

---

## 19. AUDIT DECISION

**Janavani should be treated as a multi-interface civic-governance platform under controlled convergence.**

The repository is already substantially beyond a Telegram-only project, but the implementation is not yet sufficiently consolidated to call the full ecosystem production-ready.

The correct next move is **deeper verification and controlled convergence**, not another architecture rewrite.

**No destructive action is authorised by this audit.**

---

## 20. EVIDENCE BASE

Primary repository evidence used for this audit includes:

- `docs/SOURCE_OF_TRUTH.md`
- `docs/JANAVANI_NORTH_STAR.md`
- `docs/MASTER_TASK_CHECKLIST.md`
- `docs/MASTER_TASK_CHECKLIST_STATUS_2026-08-23.md`
- `docs/CAPABILITY_REGISTRY.md`
- `docs/DATA_CONTRACTS.md`
- `docs/REPOSITORY_RECONCILIATION_AUDIT_2026-08-23.md`
- `docs/DEPLOYMENT_TOPOLOGY_AUDIT_2026-08-23.md`
- `src/web/canonical_app.py`
- `tests/test_canonical_app.py`
- current `main` commit history and GitHub PR/CI state.

---

**AUDIT STATUS: COMPLETE — RECONNAISSANCE / DOCUMENTATION PHASE**  
**APPLICATION CODE CHANGES: NONE**  
**DESTRUCTIVE ACTIONS: NONE**  
**NEXT: SYNCHRONISE MASTER CHECKLIST + CONTINUE RUNTIME/CAPABILITY VERIFICATION**
