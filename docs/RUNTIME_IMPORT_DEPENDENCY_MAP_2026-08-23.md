# JANAVANI — RUNTIME / IMPORT / DEPENDENCY MAP

**Date:** 23 August 2026
**Mode:** READ-ONLY STATIC RUNTIME RECONCILIATION
**Repository:** `netzen-abm/janavani`
**Purpose:** Establish the currently observable executable entry points, import chains, service/storage dependencies, deployment targets and architectural conflicts before any migration, archive or deletion.

> **Evidence rule:** This document is based on the actual repository files inspected through GitHub. It is a static/runtime-configuration map, not proof that every path has successfully executed in a live environment. Execution evidence remains a separate task.

---

# 1. EXECUTIVE FINDING

The repository currently contains **multiple competing runtime paths**.

The most important conflict is:

```text
DEPLOYMENT CONFIGURATION
        │
        ├── render.yaml → python3 src/web.py
        │
        ├── entrypoint.sh → python -m src.bot_telegram + python -m src.web
        │
        └── Dockerfile → uvicorn src.web.app:app
                                      │
                                      └── api.agent_api:app in second Docker stage
```

Therefore there is **not yet one unambiguous canonical production entry point**.

This is the highest-priority convergence issue discovered in this phase.

---

# 2. OBSERVED ENTRY POINTS

## E-01 — Legacy/root test entry point

`src/main.py`

Observed imports:

```text
src/main.py
 ├─ tools.search_directory.search_office
 ├─ tools.rate_office.save_rating
 ├─ tools.generate_pdf.generate_complaint_pdf
 └─ legal_brain.get_legal_advice
```

The file describes itself as a whole-system test and executes directory search, rating persistence, PDF generation and legal advice.

**Status:** TEST/LEGACY ENTRY — NOT ESTABLISHED AS PRODUCTION ENTRY.

---

## E-02 — Telegram production-style entry point

`src/bot_telegram.py`

Observed imports:

```text
src/bot_telegram.py
 ├─ core.config.Config
 ├─ commands.check.check
 ├─ commands.start.start
 ├─ commands.search.search
 ├─ commands.rate.rate
 ├─ commands.complaint.complaint
 ├─ conversation.router.route
 └─ conversation.steps.format.handle_format
```

Runtime behavior:

```text
Telegram update
      ↓
command handlers / message handler
      ↓
conversation.router
      ↓
conversation.engine
      ↓
state registry / workflow handler
```

`Config.TELEGRAM_BOT_TOKEN` is environment sourced.

**Status:** ACTIVE-CANDIDATE CHANNEL ENTRY; runtime execution still requires test evidence.

---

## E-03 — Legacy/simple Flask web entry point

`src/web.py`

Observed imports:

```text
src/web.py
 ├─ flask
 ├─ core.config.Config
 └─ database.supabase.supabase
```

It exposes:

```text
/
/health
/supabase
```

When run as `__main__`, it also starts `src/bot_telegram.py` as a subprocess.

**Status:** ACTIVE DEPLOYMENT-CANDIDATE / LEGACY WEB PATH.

---

## E-04 — FastAPI service gateway

`src/web/app.py`

Observed imports include:

```text
FastAPI
src.services.legal_agent.JanavaniLegalAgent
src.utils.validators
src.storage.cache
src.storage.analytics
src.services.emergency_sos.JanavaniEmergencySOSEngine
src.web.feedback_router
src.web.legislative_router
src.web.constitutional_router
src.web.land_router
src.conversation.engine
```

It contains multiple repeated FastAPI/Flask application definitions in the same file, including repeated `app = FastAPI(...)`, repeated routers and later Flask application definitions.

**Finding:** This file is a major architectural collision point. The source as currently stored should not be treated as a clean single ASGI application without refactoring/verification.

**Status:** HIGH-RISK / REQUIRES CONVERGENCE.

---

## E-05 — Web MVP entry point

`src/web_mvp/main.py`

Observed architecture:

```text
Web MVP
   ↓
JanavaniWebAPIClient
   ↓
backend service
```

It exposes citizen issue submission and constitutional/bill-review flows and supports PDF/DOCX selection at the UI level.

**Important:** UI offering DOCX does not establish that the backend can generate DOCX. The canonical document service currently reports DOCX as not implemented.

**Status:** PARALLEL WEB IMPLEMENTATION — REQUIRES CANONICALIZATION.

---

## E-06 — Agent/RAG POC API

`api/agent_api.py`

Observed endpoints:

```text
POST /ingest
POST /query
POST /generate_complaint
```

Observed dependencies:

```text
api.agent_api
 ├─ services.rag_agent
 └─ services.agent_runner
```

The module explicitly identifies itself as an SLM + RAG POC.

**Status:** EXPERIMENTAL/POC — SHOULD REMAIN ISOLATED FROM CORE UNTIL CONTRACTED.

---

# 3. DEPLOYMENT PATHS

## D-01 — Render

`render.yaml` specifies:

```text
startCommand: python3 src/web.py
```

Therefore the declared Render service points to the legacy/simple Flask path.

**Status:** DEPLOYMENT TARGET IDENTIFIED.

---

## D-02 — Shell entrypoint

`entrypoint.sh` specifies:

```text
python -m src.bot_telegram &
python -m src.web
```

Therefore container execution starts Telegram and then runs the simple Flask web server.

**Status:** DEPLOYMENT PATH IDENTIFIED.

---

## D-03 — Dockerfile

The root `Dockerfile` contains two `FROM` instructions and therefore defines two Docker build stages, but without explicit stage names/selection in the observed file.

The first stage points to:

```text
uvicorn src.web.app:app
```

The second stage points to:

```text
uvicorn api.agent_api:app
```

The effective final image therefore requires careful Docker-stage verification; it cannot be assumed that the first stage is the deployed runtime.

**Status:** HIGH-RISK DEPLOYMENT AMBIGUITY.

---

# 4. TELEGRAM IMPORT CHAIN

```text
src/bot_telegram.py
        │
        ├── /start ───────→ commands/start.py
        │
        ├── /search ──────→ commands/search.py
        │                         │
        │                         └→ services/search_directory.py
        │                                  │
        │                                  └→ database/offices.csv
        │
        ├── /rate ────────→ commands/rate.py
        │                         │
        │                         └→ services/rate_office.py
        │
        ├── /complaint ──→ commands/complaint.py
        │                         │
        │                         └→ conversation.state
        │
        └── text/callback
                ↓
        conversation.router
                ↓
        conversation.engine
                ↓
        conversation.state
                ↓
        engine.state_registry
                ↓
        workflow handlers
```

The Telegram channel is therefore not merely a placeholder; there is a real command/workflow structure.

**But:** the underlying storage and document layers are still not fully reconciled with the new Data Contracts.

---

# 5. DIRECTORY DEPENDENCY

Observed path:

```text
Telegram /search
      ↓
commands/search.py
      ↓
services/search_directory.py
      ↓
pandas.read_csv()
      ↓
database/offices.csv
```

The service returns office ID, name, address, officer role and email.

### Architectural gap

The canonical `GovernmentOffice` contract requires:

- organisation relationship;
- jurisdiction;
- multiple postal addresses;
- multiple contact points;
- official URLs;
- source references;
- verification status;
- last verification timestamp.

The CSV-backed service is materially narrower.

**Status:** LEGACY/FOUNDATION DIRECTORY PATH — MIGRATION REQUIRED LATER.

---

# 6. DOCUMENT DEPENDENCY

Observed canonical-looking service:

```text
services/document_service.py
       ↓
documents/complaint_builder.py
       ↓
legal_brain.get_legal_advice()
       ↓
documents/generate_pdf.py
```

The document service supports:

```text
PDF → implemented path
DOCX → explicit "not implemented yet"
```

### Important mismatch

The new master checklist requires:

```text
PDF
DOCX
To postal address
To email
CC postal address
CC email
user correction
verification
submission state
archive
```

The currently observed service does not yet satisfy the full canonical document contract.

**Status:** IMPLEMENTATION PRESENT / CONTRACT INCOMPLETE.

---

# 7. AI DEPENDENCY MAP

## A-01 — Legal agent

`src/services/legal_agent.py`

Observed external AI dependencies:

```text
Citizen issue
   ↓
Indic-language translation via Hugging Face
   ↓
OpenRouter request
   ↓
structured JSON legal-document output
```

Configuration is read from `src/core/settings.py`.

### Finding

The repository already contains an AI provider abstraction direction, but the implementation is not yet the canonical RAG/SLM/LLM architecture.

---

## A-02 — RAG POC

`api/agent_api.py` explicitly exposes FAISS ingest/query and complaint generation.

This is a separate POC path from the root legal-agent path.

**Decision:** Keep as experimental until the canonical AI architecture defines its role.

---

# 8. STORAGE DEPENDENCY MAP

Observed storage systems include:

```text
A. database/offices.csv
B. database/complaints.jsonl
C. database/ratings.jsonl
D. src/storage/cache.py
E. src/storage/analytics.py
F. src/storage/supabase.py
G. Redis references in emergency/agent services
H. RAG/FAISS POC storage
```

### Finding

There is no single proven persistence authority yet.

The Data Contracts therefore must remain design-level until the storage ownership map is complete.

---

# 9. SOS DEPENDENCY MAP

Observed path:

```text
src/web/app.py
       ↓
JanavaniEmergencySOSEngine
       ↓
Redis
       ↓
volatile cache deletion
       ↓
Nostr emergency event construction
```

### Critical architectural discrepancy

The canonical SOS contract requires:

```text
SOS creation
→ trusted contacts
→ authority choice
→ delivery state
→ offline queue
→ mesh
→ satellite
→ acknowledgement
```

The currently inspected SOS engine instead focuses on a **crisis-lockdown / volatile-cache wipe** behavior and constructs a Nostr event.

This should **not** be treated as the completed citizen SOS system.

### Safety concern requiring later design review

The engine contains destructive cache deletion behavior. The new archive-first principle does not prohibit intentional volatile-data expiry in a specifically designed emergency security function, but that behavior requires an explicit threat model and data-retention policy before being treated as canonical.

**Status:** EXPERIMENTAL SECURITY/SOS PATH — NOT CANONICAL YET.

---

# 10. SECURITY FINDINGS FROM STATIC INSPECTION

## SEC-01 — Hardcoded interface tokens

`src/web/app.py` currently contains literal interface-token values in source.

**Severity:** CRITICAL if these are actual credentials/secrets.

**Required action:** Replace with secure secret/configuration management before production exposure. Do not simply move the same values into another committed file.

## SEC-02 — Multiple authentication implementations

`src/web/app.py` contains repeated interface-authentication definitions and multiple application definitions.

**Severity:** HIGH.

**Required action:** One canonical authentication middleware/dependency.

## SEC-03 — Runtime truthfulness

SOS and external delivery paths must distinguish:

```text
created
queued
sent
received
acknowledged
failed
```

This is required by the Data Contracts.

## SEC-04 — POC/API isolation

`api/agent_api.py` exposes ingest/query/generation endpoints without evidence here of the full production authentication, authorization, rate limiting, provenance and audit controls required by the canonical ecosystem.

**Status:** POC only until verified.

---

# 11. DEPENDENCY CONFLICT MATRIX

| Responsibility | Observed implementation(s) | Canonical direction | Current decision |
|---|---|---|---|
| Web runtime | `src/web.py`, `src/web/app.py`, `src/web_mvp/main.py` | One channel-independent web client/API boundary | Reconcile |
| API gateway | `src/web/app.py`, `api/agent_api.py` | Capability API boundary | Separate core vs POC |
| Telegram | `src/bot_telegram.py` | Channel adapter | Preserve |
| Conversation | `conversation/router.py`, `conversation/engine.py` | Shared workflow engine | Preserve/reconcile |
| Directory | CSV service + Supabase | Versioned GovernmentOffice contract | Migrate later |
| Documents | document service + web_mvp client path | Canonical document service | Reconcile |
| AI | legal agent + RAG POC | Provider/model abstraction + RAG | Separate and map |
| Storage | CSV/JSONL/Supabase/Redis/FAISS | Contract-driven storage boundary | Map ownership |
| SOS | emergency_sos + future mesh/satellite | Multi-transport SOS | Redesign around canonical contract |
| Deployment | Render/entrypoint/Docker | One canonical deployment | Resolve |

---

# 12. CAPABILITY-TO-ENTRY-POINT INITIAL MAP

| Capability | Candidate entry point | Supporting modules | Evidence status |
|---|---|---|---|
| Civic complaint | Telegram `/complaint` | conversation/workflow/document | PARTIAL |
| Office search | Telegram `/search` | search_directory + CSV | PRESENT / LEGACY |
| Office rating | Telegram `/rate` | rate_office | PRESENT / VERIFY |
| PDF complaint | document service | complaint_builder + PDF generator | PRESENT |
| DOCX | Web MVP UI | backend document layer | UI ONLY / NOT IMPLEMENTED |
| Legal AI draft | web/app gateway | legal_agent | PRESENT / VERIFY |
| RAG | api/agent_api | rag_agent | POC |
| Legislative review | web_mvp + router | legislative router | PRESENT / VERIFY |
| Constitutional review | web_mvp + router | constitutional router | PRESENT / VERIFY |
| Land mapping | web/app router | land router | PRESENT / VERIFY |
| SOS | web/app | emergency_sos + Redis | EXPERIMENTAL |
| Mesh SOS | V2 materials | mesh components | NOT E2E VERIFIED |
| Satellite SOS | architecture | no verified production adapter in inspected path | DESIGN |
| Government alerts | architecture/contracts | no verified runtime path | DESIGN |
| Whistleblower | architecture/contracts | no verified runtime path | DESIGN |
| Finance transparency | data contracts | no verified runtime path | DESIGN |

---

# 13. RUNTIME VERIFICATION GATES

The next execution phase must test each candidate entry point using:

```text
IMPORT TEST
   ↓
STARTUP TEST
   ↓
HEALTH TEST
   ↓
FUNCTION TEST
   ↓
STORAGE TEST
   ↓
EXTERNAL-INTEGRATION TEST
   ↓
SECURITY TEST
   ↓
FAILURE TEST
   ↓
EVIDENCE COMMIT
```

No production claim should be made before these gates are satisfied for the relevant capability.

---

# 14. IMMEDIATE HIGH-PRIORITY FINDINGS

### P0 — Deployment/runtime ambiguity

Resolve `src/web.py` vs `src/web/app.py` vs `api/agent_api.py` as deployment targets.

### P0 — `src/web/app.py` structural duplication

It contains repeated application definitions and overlapping implementations.

### P0 — Authentication secret hygiene

Literal interface tokens must not remain as production credentials in source.

### P1 — Document contract mismatch

DOCX and full To/CC/address/verification workflow remain incomplete in the observed canonical service.

### P1 — Storage ownership

CSV/JSONL/Supabase/Redis/FAISS all exist; ownership must be defined before migration.

### P1 — SOS contract mismatch

Current emergency engine is not yet equivalent to the canonical multi-transport citizen SOS design.

### P1 — AI path duplication

Legal-agent AI and RAG POC need explicit roles and boundaries.

---

# 15. DO NOT DELETE / ARCHIVE YET

The following are **not** archive-approved:

- `src/web.py`
- `src/web/app.py`
- `src/web_mvp/`
- `api/agent_api.py`
- root `src/` service modules
- `janavani_v2/`
- `janavani_v3/`
- legacy storage files

They may be redundant, but redundancy has not yet been proven safe to remove.

---

# 16. NEXT MAP

The next required document is:

`docs/CAPABILITY_REPOSITORY_TEST_DEPLOYMENT_MAP_2026-08-23.md`

It will map each canonical capability to:

```text
Capability ID
→ source module
→ data contract
→ entry point
→ channel
→ storage
→ external dependency
→ tests
→ CI
→ deployment
→ security review
→ actual verification status
```

---

# 17. STATUS

**M2-A static runtime/import/deployment mapping:** SUBSTANTIALLY COMPLETE

**Live execution:** NOT YET PERFORMED

**M2-B capability repository mapping:** NEXT

**M2-C storage ownership mapping:** NEXT AFTER M2-B

**Destructive changes:** NONE AUTHORISED

**END**
