# Programming / Code-Line Audit — 2026-09-21

## Scope

Audited the current `main` runtime Python surface and the canonical WebApp/Telegram/provider/capability path. The audit includes file size, line count, construction paths, and architecture-boundary risks.

## Canonical files reviewed

| File | Lines | Assessment |
|---|---:|---|
| `src/capabilities/submission.py` | 427 | **Decompose next** — consequential orchestration, reservation, delivery, outcome handling, acknowledgement, and execution validation are too concentrated. |
| `src/storage/repositories/postgres_civic_case.py` | **112** | **Decomposed** — repository orchestration retained; mapping and SQL persistence extracted. |
| `src/storage/repositories/postgres_submission_case_transaction.py` | 218 | Reviewable; retain unless a responsibility split becomes clear. |
| `src/storage/repositories/postgres_submission.py` | 204 | Reviewable; provider adapter remains bounded. |
| `src/capabilities/civic_action_vertical_slice.py` | **170** | **Decomposed** — document lifecycle extracted to dedicated helper. |
| `src/core/case_model.py` | 177 | Acceptable domain model. |
| `src/conversation/steps/generate.py` | 132 | Adapter-sized after provider/capability convergence. |
| `src/capabilities/civic_case_lifecycle.py` | 118 | Acceptable. |
| `src/capabilities/civic_case_impl.py` | 109 | Acceptable. |
| `src/platform/surface_case_composition.py` | 110 | Acceptable shared composition boundary. |
| `src/platform/composition_capabilities.py` | 91 | Acceptable factory boundary. |
| `src/platform/composition_repositories.py` | 87 | Acceptable provider boundary. |
| `src/web/composition.py` | 88 | Acceptable surface composition boundary. |
| `src/web/civic_case_router.py` | 62 | Thin adapter. |
| `src/bot_telegram.py` | 74 | Thin bootstrap/adapter boundary. |

## Duplicate construction finding and remediation

`src/web/civic_case_capability_adapter.py` was a duplicate Web-side Case capability construction path. Its only remaining consumer was a test. The file was archived first to `archive/legacy/web/civic_case_capability_adapter.py.archived-2026-09-21`, the test was migrated to the canonical `CivicCaseCapability`, and the duplicate production file was deleted.

This follows the repository rule: **archive first, delete only after evidence of replacement**.

## Telegram finding

Telegram generation previously constructed its own `ConsentCapability` and directly created its artifact repository. The generation dependency factory now accepts the canonical `ConsentCapability`, provider composition, and optional artifact/blob dependencies. The Telegram bootstrap passes the canonical surface composition into that factory.

## Remaining code-level risks

1. `src/capabilities/submission.py` is the largest canonical capability file at 427 lines. Split delivery transport orchestration, submission state transition helpers, and reconciliation/acknowledgement coordination without changing the public capability contract.
2. `src/storage/repositories/postgres_civic_case.py` is 389 lines. Split SQL mapping/query concerns from repository lifecycle/concurrency behavior if the boundary can be made explicit.
3. `src/web_mvp/main.py` remains a legacy UI surface and must not be treated as canonical WebApp infrastructure without a separate migration decision.
4. `src/web_dioxus/` and other historical/parallel surface trees require runtime reachability checks before any deletion.
5. Test-only direct capability construction is acceptable when it deliberately tests the capability itself; production surfaces must use canonical composition.

## Canonical rule

Production runtime code should follow:

`Surface Adapter → ProviderComposition → Canonical Capability → Repository/Provider`

and not:

`Surface → direct repository/provider → duplicate capability`.

## Branch hygiene

The nine sanctioned active roles are the only permitted development roles: `main`, `integration/canonical-platform`, `feat/canonical-case-kernel`, `feat/canonical-capability-execution-envelope`, `feat/canonical-civic-action-vertical-slice`, `feat/canonical-sos-contract`, `feat/capability-scoped-consent-agent-enforcement`, `audit/postgres-provider-production-gates`, and `chore/ecosystem-shared-capability-infrastructure`. Historical refs are frozen retirement candidates. Physical deletion still requires a GitHub ref-delete operation; no ref is force-moved as a substitute.


## 180-line decomposition progress

`postgres_civic_case.py` was decomposed without changing its public repository contract. Mapping/hydration moved to `postgres_civic_case_codec.py` (59 lines), and SQL persistence primitives moved to `postgres_civic_case_sql.py` (55 lines). The canonical repository façade is now 112 lines. The existing UoW, principal binding, optimistic concurrency, event persistence, and reference persistence remain in the provider path.


`postgres_case_transaction.py` was reduced from 233 to 115 lines; SQL primitives moved to `postgres_case_transaction_sql.py` (66 lines). `civic_action_vertical_slice.py` was reduced from 194 to 170 lines; document preparation/review/artifact generation moved to `civic_action_vertical_slice_document.py` (55 lines). Public orchestration methods remain available through the canonical façade.

## 2026-09-21 convergence continuation

### Service-layer cleanup

A dependency search found no active imports of the five zero-byte service stubs `ai_service.py`, `classification_service.py`, `complaint_service.py`, `language_service.py`, or `id_generator.py`. Their empty implementations were archived under `archive/legacy/services/` and the active stubs were removed. This was content-preserving retirement: no runtime implementation was deleted.

The remaining `src/services/` files require responsibility-by-responsibility migration because the directory still contains active compatibility/runtime adapters mixed with legacy-era services. No bulk deletion is authorized.

### Branch enforcement

The CI branch-budget gate now runs for pushes to every branch, not only `main`, so creation/use of an unapproved long-lived branch fails CI. The canonical `main` push gate additionally counts remote branch refs and fails unless exactly nine physical refs exist. This does not itself delete historical refs; physical deletion remains an operational GitHub administration step because the connected mutation surface does not expose branch-ref deletion.


## Service ownership verification — 2026-09-21

| File | Current lines | Decision |
|---|---:|---|
| `src/services/kml_composer.py` | 56 | Retain; live land-router caller and tests. |
| `src/services/legal_agent.py` | 96 | Retain as provider-neutral AI adapter; not legal authority. |
| `src/services/watchdog.py` | 127 | Hold/consolidate; duplicate class and no confirmed active caller. |
| `src/services/authority_service.py` | 36 | Canonical owner for authority lookup. |
| `src/services/office_service.py` | 47 | Temporary compatibility adapter; migrate consumers to canonical authority contract. |
| `src/services/search_directory.py` | 39 | Temporary text adapter; migrate consumers to structured authority capability. |

`src/services/emergency_sos.py` is 56 lines and remains transitional. Do not retire it until cache destruction, credential/session revocation, emergency delivery, evidence/context, and orchestration contracts each have explicit owners and tests.


## SOS legacy retirement verification

The legacy `src/services/emergency_sos.py` and its direct Redis test were archived before deletion. Canonical SOS already owns provider-neutral delivery and safety/privacy orchestration. Explicit transient-data destruction and credential/session revocation protocols are now defined in `src/core/sos.py`, with the storage/session implementations and dedicated security-contract tests. The legacy service is no longer an active runtime owner.


## Additional service convergence — 2026-09-21

The legacy `src/services/document_service.py` was verified at 31 lines. Exact symbol/import search found no active runtime caller; only its dedicated fail-closed legacy test imported it. The service and test were archived before retirement. Canonical document generation remains owned by the shared civic-action capability.
