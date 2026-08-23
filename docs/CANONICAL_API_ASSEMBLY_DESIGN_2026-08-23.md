# JANAVANI — CANONICAL API ASSEMBLY DESIGN

**Date:** 23 August 2026  
**Phase:** M3-D  
**Mode:** DESIGN / NO APPLICATION REFACTORING  
**Repository:** `netzen-abm/janavani`

## 1. Objective

Define the controlled target architecture for replacing the historical, concatenated FastAPI generations in `src/web/app.py` with one canonical platform API assembly while preserving compatibility and avoiding destructive changes.

This document is a design gate. It does **not** authorize route deletion, renaming, migration, or provider cutover.

---

## 2. Current state

The route audit identified five principal domain families currently exposed around the API candidate:

```text
agent
feedback
legislative
constitutional
land
```

The current `src/web/app.py` contains repeated FastAPI application/router generations. The route ownership audit also identified hard-coded interface tokens and high-impact dispatch/SOS routes requiring stronger cross-cutting controls.

Therefore the first implementation objective is **structural convergence**, not feature expansion.

---

# 3. Target package boundary

The target structure is:

```text
src/web/
│
├── app.py                         # ONLY FastAPI assembly
│
├── dependencies/
│   ├── auth.py                    # authentication dependencies
│   ├── authorization.py           # permission/policy dependencies
│   └── request_context.py         # request/correlation context
│
├── middleware/
│   ├── correlation.py
│   ├── security.py
│   └── observability.py
│
├── routes/
│   ├── agent.py
│   ├── feedback.py
│   ├── legislative.py
│   ├── constitutional.py
│   ├── land.py
│   └── sos.py
│
├── schemas/
│   ├── agent.py
│   ├── feedback.py
│   ├── legislative.py
│   ├── constitutional.py
│   ├── land.py
│   └── sos.py
│
└── compatibility/
    └── legacy_routes.py
```

The exact filenames may be adjusted to existing repository conventions during implementation. The architectural rule is that `app.py` becomes an **assembly root**, not a business-logic container.

---

# 4. Canonical application assembly

The target `app.py` responsibility is deliberately small:

```text
create FastAPI app
        ↓
configure middleware
        ↓
register exception handlers
        ↓
register health/readiness endpoints
        ↓
register canonical routers
        ↓
register compatibility router if required
        ↓
return app
```

It must NOT contain:

- document-generation business logic;
- SMTP implementation;
- direct Redis operations;
- direct database operations;
- AI prompting logic;
- SOS escalation logic;
- representative lookup implementation;
- geospatial conversion implementation.

Those belong to services/adapters.

---

# 5. Domain route boundaries

## Agent

```text
routes/agent.py
      ↓
AgentWorkflowService
      ↓
LegalAgent / DocumentService / TransientStorage
```

Responsibilities:

- citizen document workflow;
- drafting orchestration;
- temporary retrieval;
- agent metrics where appropriate.

The route layer should validate input and authorization, then delegate.

## Feedback

```text
routes/feedback.py
      ↓
FeedbackService
      ↓
FeedbackRepository / Analytics
```

No route should instantiate Redis clients directly.

## Legislative

```text
routes/legislative.py
      ↓
RepresentativeService
      ↓
DirectoryRepository

routes/legislative.py
      ↓
DispatchService
      ↓
DocumentService + NotificationAdapter
```

Document composition and SMTP/notification delivery must be separate operations.

## Constitutional

```text
routes/constitutional.py
      ↓
ConstitutionalWorkflowService
      ├── BillMonitor
      ├── DocumentService
      └── NotificationService
```

Draft generation and dispatch remain separate commands.

## Land

```text
routes/land.py
      ↓
LandMappingService
      ├── GeodeticConverter
      └── KmlComposer
```

## SOS

```text
routes/sos.py
      ↓
SOSOrchestrator
      ├── consent/policy
      ├── location policy
      ├── escalation policy
      ├── notification adapters
      ├── audit ledger
      └── transport adapters
```

SOS is intentionally isolated because it has materially higher consequence than ordinary API requests.

---

# 6. Authentication and authorization

The existing interface-token approach must not remain embedded in source code.

Target flow:

```text
Request
  ↓
Authentication
  ↓
Identity / interface context
  ↓
Authorization policy
  ↓
Domain permission
  ↓
Service
```

Authentication answers:

> Who/what is making this request?

Authorization answers:

> Is this actor allowed to perform this operation on this resource?

Interface identity must not be treated as citizen identity.

Future authentication mechanisms may include:

- signed interface credentials;
- citizen session credentials;
- OAuth/OIDC where appropriate;
- bot-specific identity;
- mobile device/session identity;
- offline signed capability tokens.

The exact mechanism is a later security-design decision.

---

# 7. Storage boundary

Routes must not directly construct storage clients.

Target:

```text
Route
 ↓
Service
 ↓
Repository / StoragePort
 ↓
Implementation
 ├── PostgreSQL
 ├── Redis
 ├── Object storage
 └── local/offline store
```

This supports the broader Janavani requirement that cloud, local and offline deployments can share the same domain services while changing only adapters.

---

# 8. AI boundary

The API assembly must not embed LLM/RAG/SLM implementation details.

Target:

```text
Domain Service
      ↓
AIService interface
      ↓
AI Orchestrator
      ├── RAG
      ├── SLM
      ├── LLM
      └── deterministic fallback
```

`api/agent_api.py` can remain a specialised AI/RAG service during transition.

The platform should call AI through a stable internal service contract rather than coupling routes to a particular model provider.

---

# 9. Document boundary

Document generation must become a dedicated service:

```text
DocumentService
 ├── PDF
 ├── DOCX
 ├── metadata
 ├── validation
 └── evidence/provenance
```

Dispatch must consume an already-generated, validated document rather than silently regenerating it.

This supports the project requirement that citizens can generate downloadable PDF/DOCX documents with prefilled recipient information and later correct recipient data without coupling document generation to delivery.

---

# 10. Notification boundary

Email, Telegram, WhatsApp, Messenger, SMS, push and future channels should use adapters:

```text
NotificationService
       │
       ├── EmailAdapter
       ├── TelegramAdapter
       ├── WhatsAppAdapter
       ├── MessengerAdapter
       ├── SMSAdapter
       └── PushAdapter
```

A citizen workflow should request:

```text
send(notification)
```

rather than knowing SMTP/Telegram/WhatsApp implementation details.

---

# 11. Compatibility strategy

We must preserve existing clients during convergence.

Target:

```text
Legacy route
     ↓
Compatibility adapter
     ↓
Canonical service
```

This allows old clients to continue working while new clients use the canonical domain routes.

A route may only be removed after:

1. reference inventory;
2. usage evidence;
3. replacement route exists;
4. migration completed;
5. tests pass;
6. deprecation period completed;
7. rollback path exists.

Only then:

```text
DEPRECATE → ARCHIVE → DELETE
```

---

# 12. Security classification

| Domain | Risk | Required control |
|---|---|---|
| Feedback | Medium | authentication + abuse/rate controls |
| Directory | Low/Medium | source integrity + freshness |
| Document draft | High | identity + privacy + audit |
| Email dispatch | High | explicit authorization + recipient verification + audit |
| Constitutional dispatch | High | authorization + provenance + audit |
| Land mapping | High | input validation + coordinate integrity |
| SOS | Critical | consent/policy + escalation + audit + failure handling |
| Admin | Critical | strong authentication + RBAC/ABAC + audit |

---

# 13. Observability boundary

Every canonical request should be traceable without exposing sensitive citizen content.

Target event fields:

```text
request_id
interface
actor/session identifier (privacy-safe)
domain
operation
result
latency
error class
policy decision
created_at
```

Sensitive document content and raw personal information should not be written to ordinary application logs.

---

# 14. Health model

The platform should expose separate health concepts:

```text
/liveness
    process is alive

/readiness
    required dependencies available

/version
    deployed build identity
```

A dependency failure must not be hidden behind a simple process-alive endpoint.

---

# 15. Implementation sequence

## M3-D.1 — Freeze current source

Create a verified snapshot before modifying `src/web/app.py`.

## M3-D.2 — Extract schemas

Move request/response models into domain schema modules without changing external behavior.

## M3-D.3 — Extract routers

Create one router module per domain.

## M3-D.4 — Extract dependencies

Create unified authentication, authorization and request-context dependencies.

## M3-D.5 — Extract services

Move orchestration/business logic behind service boundaries.

## M3-D.6 — Extract adapters

Move Redis, SMTP, AI, document and external integration logic behind adapters.

## M3-D.7 — Build canonical app

Reduce `src/web/app.py` to assembly only.

## M3-D.8 — Add compatibility layer

Preserve existing external routes until migration is verified.

## M3-D.9 — Test

Run:

```text
pytest
cargo test
API smoke tests
security tests
container build
```

## M3-D.10 — Staging

Deploy only after tests pass and route parity is demonstrated.

---

# 16. Non-goals for this phase

Do NOT simultaneously:

- redesign the entire database;
- replace the AI stack;
- migrate all cloud providers;
- build mobile apps;
- implement Web3;
- rewrite every interface;
- delete legacy files.

Those are separate workstreams.

The purpose of M3-D is **API structural convergence**.

---

# 17. Acceptance criteria

M3-D implementation is complete only when:

- exactly one canonical FastAPI application is assembled;
- each active route has one owner;
- authentication is centralized;
- authorization is explicit;
- storage is accessed through defined boundaries;
- AI is accessed through a service boundary;
- document generation is isolated;
- notification delivery is isolated;
- SOS is isolated and separately audited;
- compatibility routes are documented;
- tests cover route registration and critical workflows;
- container startup uses the canonical application;
- no historical implementation is deleted merely because it is old.

---

# 18. Status

**M3-D DESIGN: COMPLETE**  
**Implementation authorization:** controlled, incremental only  
**Production approval:** NOT YET GRANTED  
**Deletion:** NONE  
**Archive:** NONE

### Next phase

**M3-D.1 — Freeze + structural extraction plan**, beginning with a verified snapshot and exact route/schema inventory before the first application-code refactor.

**END OF DOCUMENT**
