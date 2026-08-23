# JANAVANI — RUNTIME ENTRY-POINT AUDIT

**Date:** 23 August 2026  
**Phase:** M3-B.2  
**Mode:** READ-ONLY RECONCILIATION  
**Repository:** `netzen-abm/janavani`

## 1. Executive conclusion

The repository currently contains **multiple incompatible application entry-point generations**. They should not be treated as interchangeable production runtimes.

The audit identifies four materially different roles:

1. `src/web.py` — small Flask web/health/Supabase test server plus Telegram subprocess launcher.
2. `src/web/app.py` — large FastAPI agent gateway containing multiple concatenated generations and duplicate `app`/router declarations.
3. `api/agent_api.py` — focused FastAPI SLM+RAG proof-of-concept service.
4. `src/main.py` — command-line integration smoke/test script, not a web server.

**Decision:** none of these should yet be declared the final ecosystem production entry point without further convergence work. However, `src/web/app.py` is the strongest candidate for the **platform API assembly boundary**, while `api/agent_api.py` should remain a specialised AI/RAG service boundary until the platform API is cleanly assembled.

`src/web.py` should be treated as a legacy/simple Flask runtime and `src/main.py` as a development smoke script.

---

## 2. Entry-point comparison

| Entry point | Framework | Primary role observed | Major dependencies | Production status |
|---|---|---|---|---|
| `src/web.py` | Flask | basic web + health + Supabase test | `core.config`, Supabase, subprocess Telegram | LEGACY / SIMPLE |
| `src/web/app.py` | FastAPI | agent/API gateway | legal agent, privacy, cache, analytics, SOS, routers | CANDIDATE / NEEDS CLEANUP |
| `api/agent_api.py` | FastAPI | SLM + RAG POC | `services.rag_agent`, `services.agent_runner`, FAISS path | SPECIALISED POC |
| `src/main.py` | Python script | manual system test | search, rating, PDF, legal brain | TEST / LEGACY |

---

# 3. `src/web.py`

The file creates a Flask application and exposes:

- `/` home page;
- `/health` health endpoint;
- `/supabase` Supabase connectivity test.

It imports `Config` and a Supabase client. When run directly, it also starts `src/bot_telegram.py` as a subprocess before starting Flask. fileciteturn386file0

### Assessment

This is useful as a **legacy bootstrap/demo server**, but it is not a sufficient ecosystem platform API.

### Problems

- combines HTTP serving and Telegram process management;
- only exposes health/Supabase test functionality;
- does not represent the broader domain/service surface;
- coupling a bot process to the web process complicates deployment and scaling.

### Decision

**Do not select as canonical platform runtime.**

Keep until all references are mapped; later deprecate and archive if no active deployment depends on it.

---

# 4. `src/web/app.py`

The file is a FastAPI application titled `Janavani Agentic AI Service Gateway`. It includes agent routes and imports legal-agent, privacy, cache, analytics and emergency-SOS components. fileciteturn389file0

The current file is not a clean single-generation module. The fetched content shows repeated blocks that redefine:

```text
app = FastAPI(...)
router = APIRouter(...)
verify_interface_token(...)
ProcessIssueRequest(...)
process_citizen_document_workflow(...)
app.include_router(...)
```

There are also repeated imports and multiple generations of the `/draft` implementation. fileciteturn389file0

### Assessment

Despite the duplication, this file has the **broadest API/platform role** among the examined entry points.

It already acts as an integration boundary for:

- legal AI;
- privacy-preserving input handling;
- transient document state;
- analytics;
- emergency SOS;
- feedback;
- legislative routes;
- constitutional routes;
- land mapping routes.

### Major blocker

The file must be refactored into **one canonical FastAPI application assembly module** before it can safely become the production platform API.

### Decision

**CANDIDATE FOR CANONICAL PLATFORM API**, subject to controlled cleanup and test verification.

No cleanup is performed by this audit.

---

# 5. `api/agent_api.py`

This is explicitly documented as the **SLM + RAG POC**.

It exposes:

- `POST /ingest`;
- `POST /query`;
- `POST /generate_complaint`.

It imports `services.rag_agent` and `services.agent_runner` and creates its own FastAPI application titled `Janavani SLM+RAG POC`. fileciteturn390file0

### Assessment

This is a specialised AI retrieval/generation service, not the entire Janavani platform API.

### Decision

**Keep as specialised service boundary.**

Do not promote it to the ecosystem's primary API merely because its Dockerfile generation currently references it.

The future platform API may call this service through an internal adapter, or its functionality may eventually be integrated behind the canonical AI service interface.

---

# 6. `src/main.py`

`src/main.py` imports directory search, office rating, PDF generation and legal-brain functionality and executes a sequence of test operations. It prints output and generates a complaint PDF. fileciteturn393file0

### Assessment

This is a **manual integration/smoke script**, not an application server.

### Decision

**Never use as production entry point.**

Retain only while useful for tests/development; later classify for archive/deprecation.

---

# 7. Recommended canonical runtime boundary

The evidence supports this target:

```text
                    CLIENT CHANNELS
                         │
       ┌─────────────────┼──────────────────┐
       ▼                 ▼                  ▼
      Web              Mobile           Messaging
       │                 │                  │
       └─────────────────┼──────────────────┘
                         ▼
                CANONICAL FASTAPI API
                     (src/web/)
                         │
          ┌──────────────┼───────────────┐
          ▼              ▼               ▼
      Workflows       Services        Adapters
          │              │               │
          └──────────────┼───────────────┘
                         ▼
                  Storage boundary
                         │
             ┌───────────┼───────────┐
             ▼           ▼           ▼
        PostgreSQL   Object store   Redis

                 Internal AI boundary
                         │
                    AI service
                    ┌────┴────┐
                    ▼         ▼
                   RAG       SLM/LLM
```

The `src/web/app.py` package should eventually become the **clean API assembly layer**, while specialised services such as RAG remain behind explicit interfaces.

---

# 8. Required refactoring sequence

Do not rewrite all four entry points at once.

### Phase 1 — Freeze roles

Record:

- canonical candidate;
- specialised services;
- legacy runtime;
- test scripts.

### Phase 2 — Clean `src/web/app.py`

Split repeated generations into:

```text
src/web/app.py
src/web/routes/agent.py
src/web/routes/feedback.py
src/web/routes/legislative.py
src/web/routes/constitutional.py
src/web/routes/land.py
src/web/routes/sos.py
```

Use one `FastAPI()` instance and one router registration path.

### Phase 3 — Separate process responsibilities

Telegram, WhatsApp, Messenger, workers and schedulers should not be child processes of the web API.

### Phase 4 — Define service adapters

The platform API should call:

```text
legal service
RAG service
document service
SOS service
storage service
notification service
```

through stable internal interfaces.

### Phase 5 — Verify tests

Only after cleanup:

```text
pytest
cargo test
API smoke tests
health checks
container build
staging deployment
```

---

# 9. Current canonicality decision

| Component | Decision |
|---|---|
| `src/web/app.py` | **CANONICAL CANDIDATE — CLEAN FIRST** |
| `api/agent_api.py` | **SPECIALISED RAG/AI SERVICE** |
| `src/web.py` | **LEGACY WEB SERVER** |
| `src/main.py` | **TEST/SMOKE SCRIPT** |

This is an architectural classification, not permission to delete anything.

---

# 10. Deployment implication

The Docker/Render/Railway/Vercel deployment definitions must not be changed to point at a new runtime until the canonical FastAPI assembly is cleaned and verified.

In particular, changing a container from one entry point to another without first resolving the duplicate `src/web/app.py` generations would merely move the failure.

---

# 11. Next phase — M3-C

The next verification task is:

**M3-C — Canonical API Assembly Audit**

Inspect and classify every route registered by `src/web/app.py`, every imported router, and every dependency used by the API. Then produce a clean route ownership map before any refactor.

### Status

**M3-B.2 Runtime Entry-Point Audit: COMPLETE**  
**Canonical runtime candidate:** `src/web/app.py`  
**Production declaration:** NOT YET APPROVED  
**Destructive actions:** NONE  
**Archive actions:** NONE

**END OF DOCUMENT**
