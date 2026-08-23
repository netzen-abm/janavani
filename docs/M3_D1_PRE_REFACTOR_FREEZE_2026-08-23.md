# JANAVANI — M3-D.1 PRE-REFACTOR FREEZE

**Date:** 23 August 2026  
**Phase:** M3-D.1  
**Mode:** READ-ONLY FREEZE / REFACTOR GATE  
**Repository:** `netzen-abm/janavani`

## 1. Freeze objective

Establish a verified baseline before any structural refactoring of the canonical FastAPI candidate.

The current `src/web/app.py` is confirmed to contain repeated application generations, repeated imports, repeated token validation definitions, and repeated router/application assembly. The current source therefore must be preserved as the pre-refactor baseline. fileciteturn402file0

**No application-code mutation is authorized by this document.**

---

## 2. Baseline target

Primary file under controlled refactor:

```text
src/web/app.py
```

Current blob SHA at audit time:

```text
c091151802b1aa61d4631585ecc0b9b004efa3dd
```

This SHA is the verification anchor for the source version inspected in this step. fileciteturn402file0

---

## 3. Verified structural findings

The inspected source contains at least these repeated structures:

```text
FastAPI application creation
APIRouter creation
INTERFACE_API_KEY_HEADER
VALID_INTERFACE_TOKENS
verify_interface_token()
ProcessIssueRequest
/draft workflow
app.include_router(...)
```

The first generation includes the SOS route and directly creates a Redis client inside the authentication function. A later generation adds feedback, legislative, constitutional and land routers. fileciteturn402file0

This confirms the earlier architectural finding: `src/web/app.py` is a concatenation of historical generations rather than a clean canonical assembly root.

---

# 4. Pre-refactor route inventory

The known route families from the completed M3-C audit are preserved as the migration baseline:

```text
/api/v1/agent
    POST /trigger-sos
    POST /draft
    GET  /retrieve/{tracking_id}
    GET  /metrics

/api/v1/feedback
    POST /submit
    GET  /summary/{office_id}

/api/v1/legislative
    GET  /directory/{constituency_code}
    POST /dispatch-email

/api/v1/constitutional
    GET  /bill/{bill_code}
    POST /generate-objection

/api/v1/land
    POST /compile-kml
```

These are the current documented migration targets, not a claim that every historical duplicate is simultaneously active at runtime.

---

# 5. Pre-refactor dependency inventory

The current API assembly imports or instantiates functionality across:

```text
src.services.legal_agent
src.utils.validators
src.storage.cache
src.storage.analytics
src.services.emergency_sos
src.web.feedback_router
src.web.legislative_router
src.web.constitutional_router
src.web.land_router
Redis
FastAPI
Pydantic
```

The first inspected generation directly imports `redis` inside `verify_interface_token()` and uses environment configuration for the Redis host. fileciteturn402file0

---

# 6. Refactor invariants

The first extraction must preserve:

1. Existing external route paths.
2. Existing HTTP methods.
3. Existing request/response contract unless a test-backed compatibility decision is made.
4. Existing domain service behavior.
5. Existing security intent, while removing insecure implementation details in a later controlled step.
6. Existing citizen workflow semantics.
7. Existing document generation behavior.
8. Existing SOS behavior until separately security-reviewed.

No simultaneous feature expansion is permitted during the first extraction.

---

# 7. First extraction boundary

The first implementation should be limited to **assembly and route ownership**, not business-logic redesign.

Target:

```text
src/web/app.py
        │
        ├── create app
        ├── configure middleware/dependencies
        ├── include routers
        └── health/readiness
```

Domain implementation remains in its current modules until each extraction is individually verified.

---

# 8. First extraction candidate

The safest first route family to extract is the **feedback router**, because it is already a distinct module:

```text
src/web/feedback_router.py
```

The first change should therefore demonstrate that:

```text
canonical app
   ↓
feedback router
   ↓
existing FeedbackService behavior
```

can be assembled without changing the public route contract.

This is preferable to beginning with SOS, legal drafting, or dispatch because those are higher-consequence workflows.

---

# 9. Test gate before extraction

Before changing `src/web/app.py`, the following must be captured from the current repository state where execution infrastructure permits:

```text
Python tests
API import test
route registration test
feedback route smoke test
Rust package test
```

If a test cannot run because of missing infrastructure/dependencies, record the blocker rather than manufacturing a passing result.

---

# 10. Change-control rule

Each structural extraction must be one bounded change:

```text
FETCH CURRENT FILE
      ↓
MAKE ONE CHANGE
      ↓
VERIFY DIFF
      ↓
RUN TESTS
      ↓
COMMIT
      ↓
UPDATE MASTER CHECKLIST
```

Do not perform a large rewrite of `src/web/app.py` in one operation.

---

# 11. Rollback rule

Every extraction commit must be independently reversible.

The previous source remains recoverable through Git history.

No destructive deletion of historical source is permitted until route parity and production behavior have been demonstrated.

---

# 12. Acceptance criteria for M3-D.1

M3-D.1 is considered complete when:

- baseline file has been fetched from the repository;
- baseline SHA is recorded;
- route families are recorded;
- dependency families are recorded;
- duplicate-generation problem is confirmed;
- first extraction boundary is selected;
- no application code has been modified in the freeze step;
- next change is explicitly bounded.

**All criteria are satisfied by this document.**

---

# 13. Next phase

## M3-D.2 — First controlled extraction

Implement **only the feedback-router assembly extraction**, after re-fetching the current `src/web/app.py` and `src/web/feedback_router.py` immediately before the write.

Then:

```text
verify route parity
→ run targeted tests
→ inspect diff
→ commit
→ update master checklist
```

**M3-D.1 STATUS: COMPLETE**  
**Application code changed:** NO  
**Baseline SHA recorded:** YES  
**Destructive action:** NONE  
**Archive action:** NONE

**END OF DOCUMENT**
