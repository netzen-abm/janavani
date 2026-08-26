# Janavani Known Failures Register

**Status:** Authoritative transparency register  
**Date:** 2026-08-26

This register exists so failures remain visible until evidence demonstrates resolution. A failure must not be hidden by excluding a check, weakening a test, replacing real verification with a mock, or relabeling an implementation gap as optional.

## Classification

- **FAILED** — executable verification currently fails.
- **INVALID-CI** — the verification workflow/configuration itself is defective and therefore cannot provide valid evidence.
- **BLOCKED** — verification cannot proceed because a prerequisite is unavailable or broken.
- **UNVERIFIED** — no sufficient executable evidence exists.
- **PARTIALLY VERIFIED** — some material behavior is verified but important paths remain unverified.

## Current known failures

| ID | Area | Finding | Classification | Evidence / next action |
|---|---|---|---|---|
| KF-001 | Canonical tests | Local SLM prompt test and implementation disagree on the required anti-chat wording/boundary. | FAILED | Fix the implementation contract without weakening the test; rerun canonical CI. |
| KF-002 | Component CI | `setup-python` received `python-python` rather than `python-version`, so the requested Python version was not applied. | INVALID-CI | Correct workflow input and rerun. |
| KF-003 | Component CI | Test collection lacks `reportlab`. | INVALID-CI | Component workflow must consume the authoritative dependency contract. |
| KF-004 | Component CI | Test collection lacks `python-docx`. | INVALID-CI | Same dependency convergence action as KF-003. |
| KF-005 | Component CI | Test collection lacks `supabase`. | INVALID-CI | Same dependency convergence action as KF-003. |
| KF-006 | Python compatibility | Starlette/httpx compatibility warning remains in the canonical environment. | UNVERIFIED | Determine compatible pinned versions and add explicit compatibility verification. |
| KF-007 | Redis API | Redis `setex` deprecation warning remains in test/runtime evidence. | UNVERIFIED | Trace the call site, migrate to the supported API, and retain behavior tests. |
| KF-008 | M3-B release gate | Runtime/deployment evidence is not yet sufficient to close M3-B. | BLOCKED | Complete authoritative startup, container, Compose, deployment-target and workflow evidence. |
| KF-009 | SOS transport | Reticulum adapter is unavailable; SOS must not claim offline mesh broadcast success. | UNVERIFIED | Implement and verify a real Reticulum adapter before enabling offline SOS transport. |
| KF-010 | SOS online delivery | Current client has no evidence that backend acceptance equals emergency delivery. | UNVERIFIED | Define delivery acknowledgement/state contract and test end-to-end. |
| KF-011 | SOS configuration | Previous client embedded a fixed backend URL and interface token. | FAILED | Removed from active client; establish a secure server-side/configuration boundary before enabling online dispatch. |
| KF-012 | SOS location | Previous client fabricated a default coordinate pair. | FAILED | Removed default; require a supplied/verified location source and explicit location status. |
| KF-013 | SOS data deletion | Previous client described local storage clearing as a global cache wipe and invoked it automatically. | FAILED | Active code no longer makes that claim or auto-wipes; define explicit, consented local-data policy before adding wipe behavior. |

## Rules

A resolved item must remain in this register with:

- resolution commit;
- verification command/workflow;
- verification result;
- date resolved.

Do not delete resolved history merely because the code is fixed.

## Truthfulness requirement

The repository may have many capabilities in source code or documentation while still having unverified or failed runtime paths. Those states are intentionally visible. Capability existence, configuration, test coverage, provider reachability, and production operation are separate claims and require separate evidence.

## Safety-critical rule

Emergency/SOS behavior is not production-ready until location provenance, transport availability, backend acceptance, delivery acknowledgement, failure recovery, privacy/data-retention behavior, and user-visible state transitions have executable evidence.
