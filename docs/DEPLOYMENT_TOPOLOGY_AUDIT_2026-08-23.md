# JANAVANI — DEPLOYMENT TOPOLOGY AUDIT

**Date:** 23 August 2026  
**Phase:** M3-B  
**Mode:** READ-ONLY ARCHITECTURAL RECONCILIATION  
**Repository:** `netzen-abm/janavani`

## 1. Executive conclusion

Janavani currently contains multiple deployment descriptions and multiple application entry points. The repository does **not yet establish one unambiguous canonical production topology**.

This is a convergence problem, not merely a hosting-provider problem.

The repository contains:

- Render deployment configuration;
- Dockerfile;
- docker-compose.yml with multiple concatenated configurations;
- Dioxus frontend build configuration inside compose;
- Python web/API entry points;
- Telegram/WhatsApp/Messenger interfaces;
- historical/POC application targets;
- deployment-related GitHub workflows.

The correct immediate action is **not to delete providers or rewrite deployment files blindly**. First establish the canonical runtime boundaries.

---

## 2. Evidence reviewed

### Project architecture

`docs/PROJECT_MAP.md` identifies `src/` as the primary application tree, `storage/` as the intended persistence boundary, Web as a development priority, Telegram as an interface rather than the platform itself, and future interfaces as independent consumers of shared Janavani capabilities. fileciteturn385file0

### Dockerfile

The current Dockerfile contains **two complete Dockerfile generations**. The first uses Python 3.11 and targets `src.web.app:app`; the second uses Python 3.10 and targets `api.agent_api:app`. Because both `FROM` instructions are present, this is a multi-stage/multi-generation construction without explicit stage naming or an intentional final-stage contract. The final image therefore follows the second `FROM` section, not the first. fileciteturn383file0

### docker-compose.yml

The compose file contains multiple concatenated `version:` and `services:` configurations. It describes different generations including:

- Nginx gateway;
- `ai-agent-service`;
- Redis;
- local Ollama SLM;
- Web MVP;
- internal admin board;
- Dioxus compiler;
- an older `janavani` service;
- multiple environment-variable conventions.

This is a **high-confidence configuration convergence blocker**. fileciteturn384file0

### Render

The repository also contains Render deployment configuration. Earlier audit evidence shows it targets `python3 src/web.py`, which is a separate application entry point from the Dockerfile's `src.web.app:app` and `api.agent_api:app` targets.

---

## 3. Current deployment candidates

| Candidate | Observed role | Evidence status | Canonical status |
|---|---|---|---|
| Render | Python web runtime | Config exists | Candidate |
| Docker | Container runtime | Config exists | Candidate |
| Docker Compose | Local/self-hosted ecosystem | Config exists but duplicated | Candidate / needs rewrite |
| Vercel | External deployment status observed | Deployment failure reported | Unresolved |
| Railway | External deployment status observed | Deployment failure reported | Unresolved |
| GitHub Actions | CI/build automation | Workflow exists | CI only, not production runtime |
| Dioxus | Web frontend technology | Package/build path exists | Frontend candidate |
| Telegram | Citizen interface | Repository implementation | Interface, not platform |
| WhatsApp | Citizen interface | Repository implementation | Interface, not platform |
| Messenger | Citizen interface | Repository implementation | Interface, not platform |

The existence of a provider or configuration does not establish that it should remain in production.

---

## 4. Canonical topology recommendation

For the full ecosystem direction, the target architecture should be:

```text
                         CITIZEN CHANNELS
                              │
          ┌───────────┬───────┼────────┬───────────┐
          ▼           ▼       ▼        ▼           ▼
        Web        Android   iOS    Telegram   WhatsApp/Messenger
          │           │       │        │           │
          └───────────┴───────┴────────┴───────────┘
                              │
                              ▼
                    JANAVANI PLATFORM API
                              │
             ┌────────────────┼────────────────┐
             ▼                ▼                ▼
        Workflows          Services          AI Layer
             │                │                │
             ▼                ▼         RAG / SLM / LLM
           Domain          Documents            │
             │                │                 │
             └────────────────┼─────────────────┘
                              ▼
                     Storage / Data Layer
                              │
             ┌────────────────┼────────────────┐
             ▼                ▼                ▼
        PostgreSQL       Object Storage       Redis
        durable truth    evidence/files      ephemeral

Optional specialised infrastructure:

RAG index      → derived retrieval index
Blockchain    → evidence anchoring
Mesh/Satellite → transport
Local SLM     → privacy/offline inference
```

The essential architectural rule is:

> **Channels are clients. The Janavani platform is the shared authority.**

This directly follows the repository's own project-map principle that Web, Telegram and future interfaces must consume shared Janavani capabilities independently. fileciteturn385file0

---

## 5. Canonical runtime recommendation

### Primary application runtime

Select **one canonical Python API/application entry point**.

Current candidates include:

```text
src/web.py
src/web.app:app
api.agent_api:app
```

These must not remain competing production entry points indefinitely.

### Recommended boundary

```text
src/app/                 Application assembly
src/web/                 HTTP/API/web adapter
src/workflow/            Business workflows
src/domain/              Domain model
src/services/            Services
src/documents/           Document generation
src/storage/             Persistence boundary
src/adapters/            External integrations
```

The actual canonical module should be selected only after inspecting the three entry points and their imports/routes.

---

## 6. Container strategy

The Dockerfile should ultimately contain **one intentional production image**.

A future canonical Dockerfile should not contain unrelated historical generations such as:

```text
FROM python:3.11-slim
...

FROM python:3.10-slim
...
```

unless they are explicitly named multi-stage build targets with a deliberate final stage.

No deletion is approved by this audit. Historical content must first be classified and preserved if necessary.

---

## 7. Compose strategy

`docker-compose.yml` should ultimately contain one canonical local/self-hosted topology.

Recommended separation:

```text
compose.yml
    Core local stack

compose.dev.yml
    Development conveniences

compose.edge.yml
    Optional edge/offline/local deployment
```

Potential services:

```text
api
postgres
redis
object-storage
local-slm (optional)
web (optional)
admin (optional)
reverse-proxy (deployment-specific)
```

Dioxus compilation should be a **build/development concern**, not automatically a long-running production service.

---

## 8. Provider strategy

Do not attempt to run the same canonical production workload simultaneously on Vercel, Railway and Render unless there is an explicit multi-region/multi-provider strategy.

Recommended policy:

```text
ONE canonical production runtime
        │
        ├── optional staging
        ├── optional disaster recovery
        └── local/offline deployment profile
```

Provider choice should be based on:

- Web/API requirements;
- background worker support;
- persistent storage integration;
- regional requirements;
- privacy requirements;
- offline/local deployment requirements;
- cost;
- observability;
- operational control.

---

## 9. Offline/local ecosystem implication

Because Janavani is intended to support offline/local operation, the long-term deployment architecture should **not make cloud availability a prerequisite for every citizen workflow**.

The architecture should support a local profile containing only the capabilities required for local operation:

```text
Local Web/App
      │
Local Janavani Runtime
      │
Local encrypted data
      │
Local SLM / OCR / CV where available
      │
Sync when connectivity returns
```

This should be treated as a deliberate deployment profile, not mixed into the ordinary cloud production runtime.

---

## 10. Current blockers

### P0 — Multiple deployment definitions

Dockerfile and compose contain multiple historical generations.

### P0 — Multiple application entry points

The repository has competing runtime targets.

### P0 — Provider ambiguity

Vercel/Railway/Render roles are not yet canonically declared.

### P1 — CI versus production boundary

GitHub Actions should validate artifacts; it should not become an accidental production runtime.

### P1 — Local/offline profile not isolated

Local SLM and local deployment concerns appear inside a large historical compose file rather than a clearly separated deployment profile.

---

## 11. Safe convergence procedure

```text
1. Inventory
      ↓
2. Identify active entry points
      ↓
3. Identify active provider deployments
      ↓
4. Select canonical application runtime
      ↓
5. Select canonical production provider
      ↓
6. Create clean canonical Dockerfile
      ↓
7. Create clean canonical compose profile
      ↓
8. Validate locally
      ↓
9. Validate CI
      ↓
10. Deploy staging
      ↓
11. Smoke test
      ↓
12. Production cutover
      ↓
13. Mark legacy configurations deprecated
      ↓
14. Archive
      ↓
15. Delete only after retention/rollback approval
```

---

## 12. Decision gate

**Do not yet delete or archive:**

- Dockerfile generations;
- compose generations;
- Render configuration;
- Vercel-related configuration;
- Railway-related configuration;
- application entry points.

The next audit must establish which are actually active and what they serve.

---

# 13. Next execution phase — M3-B.2

Inspect the actual entry points:

```text
src/web.py
src/web/app.py
api/agent_api.py
src/main.py
```

For each, record:

- framework;
- routes;
- imported services;
- storage dependencies;
- environment variables;
- background processes;
- health endpoint;
- production suitability;
- tests;
- consumers/deployment references.

Then select the canonical application runtime based on evidence.

**Status:** M3-B deployment topology audit COMPLETE; M3-B.2 runtime-entry-point audit NEXT.

**No destructive action authorized by this document.**
