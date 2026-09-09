# JANAVANI — M2-B CAPABILITY → REPOSITORY → TEST → DEPLOYMENT MAP

**Date:** 9 September 2026  
**Scope:** Current `main` canonical runtime boundaries  
**Status:** INITIAL VERIFIED MAP — runtime/deployment evidence still open where explicitly marked

## Purpose

This document records the first executable mapping of the capability registry to current repository implementations, focused tests, and known deployment/runtime boundaries. It is an evidence map, not a claim that every capability is production-complete.

## Evidence rules

- Repository presence is not implementation completion.
- A test file is not passing-test evidence until CI/runtime execution is observed.
- A deployment configuration is not runtime evidence until the deployed path is verified.
- Historical `janavani_v2/` and `janavani_v3/` implementations are not canonical runtime targets.

## Current map

| Capability | Canonical repository boundary | Focused test evidence | Current deployment/runtime boundary | Status |
|---|---|---|---|---|
| CASE | `src/capabilities/civic_case.py`; `src/storage/repositories/civic_case.py` | `tests/test_civic_case_capability.py`; `tests/test_web_telegram_shared_case_contract.py` | Web: `src/web/civic_case_router.py`; Telegram composition uses shared repository/capability factories | IMPLEMENTED / VERIFYING runtime |
| CIVIC ACTION | `src/capabilities/civic_action_capability.py` | `tests/test_civic_action_capability.py`; `tests/test_civic_action_capability_shared.py` | Web civic-case adapter; Telegram composition boundary | IMPLEMENTED / VERIFYING runtime |
| AUTHORITY | `src/core/authority.py`; `src/storage/repositories/authority.py` | Focused authority tests exist in repository | Shared composition factory; Web/Telegram consumers | PARTIAL |
| DOCUMENT | `src/documents/document_contract.py`; `src/documents/renderers.py` | `tests/test_civic_action_capability.py` includes PDF/DOCX renderer coverage | Canonical civic-action document draft path | CONTRACT IMPLEMENTED / VERIFYING runtime |
| IDENTITY | `src/identity/` (`Principal`, `IdentityContext`, HTTP assertion) | Identity/auth authorization tests exist | Web HTTP boundary via `require_authenticated_identity`; Telegram identity boundary requires convergence verification | PARTIAL |
| CONSENT | `src/capabilities/civic_case.py` consent command plus identity/authorization layers | Focused capability/security tests exist | Shared Case capability; Web consent route | PARTIAL |
| EVIDENCE | `src/core/evidence.py`; evidence repositories/storage providers | Evidence-focused tests exist | Shared storage boundary; local/object providers | PARTIAL |
| AI | `src/ai/` and provider adapters | AI/provider tests exist | Shared provider boundary; exact production provider runtime remains unverified | ADAPTER / VERIFYING |
| SEARCH | shared search/provider modules | Search tests exist | Shared capability/provider boundary | PARTIAL |
| FOLLOW_UP | follow-up capability/modules | Focused tests where present | Shared capability boundary | PARTIAL |
| NOTIFICATION | notification capability/modules | Focused tests where present | Channel adapters remain consumers | PARTIAL |
| AUDIT | audit/policy modules | Focused architecture/security tests | Shared governance/evidence boundary | PARTIAL |

## Canonical application assembly

`src/web/canonical_app.py` is the current FastAPI assembly boundary. It includes the civic-case router along with the other current domain routers and exposes `/`, `/liveness`, and `/version`.

`src/web/app.py` is retained as a compatibility entry point and is not the canonical business-logic boundary.

## Storage boundary

`src/storage/repositories/provider.py` selects `memory`, `postgres`, or `supabase` behind `CivicCaseRepository`. The default outside production is `memory`; production validation requires durable providers and a PostgreSQL DSN. This protects development environments from silently acquiring an external persistence dependency.

## CI/deployment evidence currently available

The latest `main` status commit `73256de29482891b0a708a39d49374a8e4b80306` has successful:

- Architecture Guard run `34343042592`.
- Security CI run `34343042541`.

Architecture Guard executed deterministic architecture guard, cross-language conformance, archive safety evidence, and serialization schema conformance.

These runs do **not** establish that the full `run_all_tests.sh` suite passed. The canonical test orchestrator requires Python tests plus Rust core/application and Dioxus client suites, and a full-suite execution result has not yet been independently verified.

## Deployment truth still required

M2-B/M2-D remains open for:

1. actual Render production/development entry point and command;
2. actual Vercel deployment path, if/when used for Janavani;
3. Docker/local entry-point verification;
4. live `/liveness`, `/version`, civic-case API and authentication verification;
5. actual configured Case/evidence/artifact providers in each environment;
6. successful full Python/Rust/Dioxus test execution evidence;
7. Telegram runtime proof that it consumes the same canonical Case lifecycle as WebApp.

## Architectural conclusion

The current repository has crossed an important convergence threshold: the canonical Case/CivicAction path is no longer merely a design document, and duplicate case/civic-action helpers have been archived. The next engineering step is verification of the execution/deployment path, not another capability-generation rewrite.

**M2-B status: INITIAL VERIFIED MAP COMPLETE.**  
**M2-C status: STORAGE OWNERSHIP VERIFICATION REMAINS OPEN.**  
**M2-D status: LIVE RUNTIME/DEPLOYMENT VERIFICATION REMAINS OPEN.**
