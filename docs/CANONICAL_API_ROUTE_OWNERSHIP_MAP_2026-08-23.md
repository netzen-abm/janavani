# JANAVANI — CANONICAL API ROUTE OWNERSHIP MAP

**Date:** 23 August 2026  
**Phase:** M3-C  
**Mode:** READ-ONLY API ASSEMBLY AUDIT  
**Repository:** `netzen-abm/janavani`

## 1. Purpose

This document maps the API surface currently assembled around `src/web/app.py` and its imported routers. It is an ownership map, not a refactoring plan.

The objective is to establish:

- which domain owns each route;
- which service/storage dependency it uses;
- which client class is expected to consume it;
- what authentication boundary is present;
- which routes are suitable for the future canonical platform API;
- which routes should remain specialised services.

No route has been deleted, renamed, migrated, or rewritten by this audit.

---

## 2. Canonical API candidate

`src/web/app.py` is currently the strongest candidate for the platform API assembly boundary because it imports multiple domain routers and platform services. However, the file contains multiple concatenated generations of application definitions and must not yet be treated as production-ready. fileciteturn394file0

The audit therefore distinguishes **route ownership** from **production approval**.

---

# 3. Route ownership map

## A. Agent / citizen-document workflow

**Router prefix:** `/api/v1/agent`

### `POST /api/v1/agent/trigger-sos`

**Owner:** Emergency/SOS domain  
**Service:** `JanavaniEmergencySOSEngine`  
**Input:** session tracking ID + approximate coordinates  
**Auth:** `X-Janavani-Interface-Token`  
**Storage/dependency:** Redis blacklist check + SOS engine  
**Consumers:** Web/mobile/messaging interfaces  
**Risk:** **P0** — emergency functionality must have a formally reviewed security, consent, audit and escalation model before production.

The route calls `trigger_crisis_lockdown()` and treats `LOCKDOWN_FAILED` as a server error. fileciteturn394file0

### `POST /api/v1/agent/draft`

**Owner:** Legal document generation workflow  
**Services:** `PrivacyPreservingTokenizer`, `JanavaniLegalAgent`, `TransientStorageEngine`, `PrivacyPreservingAnalytics`  
**Auth:** interface token  
**Output:** generated structured legal document + tracking ID in some generations  
**Consumers:** Web/mobile/messaging  
**Status:** **CORE PLATFORM CANDIDATE**

The current source contains multiple generations of `/draft`, including differing response models and differing AI-response parsing. This is a **P0 convergence issue**. fileciteturn394file0

### `GET /api/v1/agent/retrieve/{tracking_id}`

**Owner:** transient document lifecycle  
**Service:** `TransientStorageEngine`  
**Auth:** interface token  
**Purpose:** retrieve cached generated document before expiry  
**Status:** **CORE PLATFORM CANDIDATE**

The source documents a temporary lifecycle and retrieves the cached document through the transient storage layer. fileciteturn394file0

### `GET /api/v1/agent/metrics`

**Owner:** platform analytics  
**Service:** `PrivacyPreservingAnalytics`  
**Auth:** interface token in the observed generation  
**Output:** Prometheus-style aggregate metrics  
**Consumers:** internal monitoring/operations  
**Status:** **INTERNAL PLATFORM ROUTE**

---

# 4. Feedback / accountability routes

**Router:** `src/web/feedback_router.py`  
**Prefix:** `/api/v1/feedback`

### `POST /api/v1/feedback/submit`

**Owner:** Citizen feedback/accountability  
**Validation:** `OfficeFeedbackSchema`, `ContentSanitizationEngine`  
**Storage:** Redis aggregate counters + bounded sanitized comments  
**Auth:** interface token  
**Consumers:** Web/Telegram/other independent channels  
**Status:** **CORE PLATFORM CANDIDATE**

The route deliberately records aggregate office/department metrics and bounded sanitized comments. fileciteturn398file0

### `GET /api/v1/feedback/summary/{office_id}`

**Owner:** office performance/accountability  
**Storage:** Redis  
**Auth:** none observed on this GET route  
**Output:** aggregate telemetry + recent sanitized comments  
**Status:** **PUBLIC/READ ROUTE — SECURITY REVIEW REQUIRED**

The route exposes recent sanitized comments in addition to aggregate statistics. fileciteturn398file0

---

# 5. Legislative communication routes

**Router:** `src/web/legislative_router.py`  
**Prefix:** `/api/v1/legislative`

### `GET /api/v1/legislative/directory/{constituency_code}`

**Owner:** representative directory  
**Service:** `lookup_representatives()`  
**Storage:** representative directory  
**Auth:** none observed  
**Consumers:** citizen interfaces  
**Status:** **CORE DIRECTORY ROUTE**

### `POST /api/v1/legislative/dispatch-email`

**Owner:** representative communication  
**Service:** `TransientStorageEngine`, representative directory, SMTP  
**Auth:** none observed in router  
**Function:** retrieve generated document and send formatted email to MP/MLA/LSGD target  
**Status:** **P0 SECURITY / DELIVERY REVIEW**

The route returns a compiled email body if SMTP credentials are absent and otherwise sends through SMTP. fileciteturn399file0

Before production, this route requires authenticated user intent, recipient/address verification, audit logging, retry/idempotency controls, and explicit delivery confirmation semantics.

---

# 6. Constitutional oversight routes

**Router:** `src/web/constitutional_router.py`  
**Prefix:** `/api/v1/constitutional`

### `GET /api/v1/constitutional/bill/{bill_code}`

**Owner:** legislative/constitutional monitoring  
**Service:** `fetch_active_bill_profile()`  
**Auth:** none observed  
**Status:** **PUBLIC READ CANDIDATE**

### `POST /api/v1/constitutional/generate-objection`

**Owner:** constitutional petition generation  
**Services:** bill monitor, localized headers, document engine, SMTP  
**Outputs:** PDF or DOCX download, or SMTP dispatch  
**Auth:** none observed  
**Status:** **P0 SECURITY / LEGAL REVIEW**

The route supports both PDF and DOCX generation through `MultiFormatDocumentEngine`, and email dispatch through SMTP. fileciteturn400file0

Production hardening must separate document drafting from legal determination, clearly label AI-generated analysis, authenticate dispatch, validate official destination addresses, and retain an auditable user authorization record.

---

# 7. Land / mapping routes

**Router:** `src/web/land_router.py`  
**Prefix:** `/api/v1/land`

### `POST /api/v1/land/compile-kml`

**Owner:** property-rights / mapping  
**Services:** `GeodeticConverter`, `KmlComposerEngine`  
**Input:** village + UTM plot coordinates  
**Output:** KML stream  
**Auth:** none observed  
**Status:** **SPECIALISED DOMAIN ROUTE**

The route converts UTM Zone 44N coordinates to WGS84 and constructs a KML document. fileciteturn401file0

This should later move behind a dedicated geospatial service boundary if the capability expands significantly.

---

# 8. Router inventory currently evidenced

The main source explicitly imports/uses the following router families:

```text
/api/v1/agent
/api/v1/feedback
/api/v1/legislative
/api/v1/constitutional
/api/v1/land
```

The repository also contains additional historical router generations and adapters, including volunteer, meta-feedback, WhatsApp, Telegram and other versioned trees. Search results show these in `janavani_v2` and `janavani_v3`; they must not automatically be assumed to be active in the current `src/web/app.py` runtime. fileciteturn395file0 fileciteturn396file7 fileciteturn396file8 fileciteturn396file9

---

# 9. Authentication boundary assessment

A significant cross-cutting issue is the use of hard-coded interface tokens in application source, for example:

```text
telegram-mvp-token-xyz
web-mvp-token-abc
android-client-token-123
```

These appear in the agent and feedback routers. fileciteturn394file0 fileciteturn398file0

### Required future model

```text
Citizen identity/session
        ↓
Interface authentication
        ↓
Authorization policy
        ↓
Domain permission
        ↓
Service execution
        ↓
Audit event
```

Interface identity must not be equivalent to citizen authorization.

---

# 10. Recommended route architecture

The future API should be organised by domain rather than by historical implementation generation:

```text
/api/v1
│
├── /citizens
├── /issues
├── /documents
├── /offices
├── /directory
├── /feedback
├── /legislative
├── /constitutional
├── /land
├── /sos
├── /volunteers
├── /notifications
├── /ai
└── /admin
```

This is a **target architecture**, not an instruction to rename routes immediately.

The existing routes should first be wrapped by stable domain services and then migrated through compatibility adapters.

---

# 11. P0 findings

### P0-1 — Duplicate application generations

`src/web/app.py` repeatedly creates new FastAPI applications and redefines routes. This prevents reliable route ownership and creates import/runtime ambiguity. fileciteturn394file0

### P0-2 — Hard-coded interface credentials

Authentication tokens are embedded in source. They must move to a secure credential/configuration mechanism before production. fileciteturn394file0

### P0-3 — High-impact dispatch without complete authorization boundary

Legislative and constitutional email dispatch routes do not show a unified interface authentication dependency in their routers. fileciteturn399file0 fileciteturn400file0

### P0-4 — Emergency route requires independent security review

SOS is a high-consequence workflow and must not be treated like an ordinary CRUD/API route. fileciteturn394file0

---

# 12. P1 findings

- Redis is directly instantiated inside several routers instead of being consistently injected through a platform storage boundary. fileciteturn398file0
- Legislative email generation directly mixes document composition, directory lookup, cache access and SMTP dispatch. fileciteturn399file0
- Constitutional objection generation mixes legal analysis presentation, document generation and email dispatch. fileciteturn400file0
- Land mapping is a specialised capability currently exposed directly from the main API assembly. fileciteturn401file0
- The main API file contains conflicting historical implementations, so the exact effective route set cannot safely be inferred from the source text until the file is normalized. fileciteturn394file0

---

# 13. Controlled refactoring sequence

```text
CURRENT ROUTES
     ↓
ROUTE INVENTORY
     ↓
OWNERSHIP MAP              ← THIS DOCUMENT
     ↓
SECURITY CLASSIFICATION
     ↓
SERVICE INTERFACES
     ↓
CANONICAL FASTAPI APP
     ↓
COMPATIBILITY ROUTES
     ↓
TESTS
     ↓
STAGING
     ↓
DEPRECATION
     ↓
ARCHIVE
```

Do not delete the historical route generations during this stage.

---

# 14. Next phase — M3-D

**Canonical API assembly cleanup design.**

Before modifying `src/web/app.py`, create a file-by-file extraction plan:

1. one canonical `FastAPI()` application;
2. one router module per domain;
3. shared authentication dependency;
4. service interfaces between routers and business logic;
5. storage adapters instead of direct Redis/Supabase calls;
6. document-generation service boundary;
7. notification/email dispatch service;
8. SOS isolated as a high-security subsystem;
9. compatibility layer for routes retained during migration.

**Status:** M3-C route ownership audit COMPLETE.  
**Production approval:** NOT GRANTED.  
**Destructive action:** NONE.  
**Archive action:** NONE.

**END OF DOCUMENT**
