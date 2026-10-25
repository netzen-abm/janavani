# Janavani Engineering Proof Cycle and Repository Structure Audit

**Date:** 25 October 2026  
**Status:** Review baseline; not a production acceptance certificate  
**Repository:** `netzen-abm/janavani`  
**Working review line:** `chore/ecosystem-shared-capability-infrastructure`

## Executive decision

Converge and verify the existing implementation before adding abstractions or expanding surfaces. Keep WebApp and Telegram as independent adapters over shared capabilities. Preserve cohesive domain/lifecycle/transaction logic; split only at change, trust, persistence, provider, independent runtime, or independent reuse boundaries.

The full ecosystem scope remains unchanged. This review focuses on the first production-quality civic-action slice and the infrastructure contracts that future surfaces can reuse.

## Live inventory

At review time:

- GitHub default branch: `main`.
- Physical branch inventory: **9 refs**, not the required 8.
- PR #204 remains open and draft; its latest inspected head was `7799850ad0ceede7386364e8ccb4e334f74fdd83`.
- PR #213 remains open; its latest inspected head was `d036839730968771e0db6d043eb2c85ad9531a88`.
- PR #204's earlier head `449b483cc1da7a15f9b4dcbd418630ed692cfc57` had seven successful workflow runs. Later OIDC changes at `7799850ad0ceede7386364e8ccb4e334f74fdd83` must be evaluated on their own exact-SHA checks; previous green runs do not certify the later head.
- The active `main` ruleset (ID `25706799`) showed zero required approving reviews, no required Code Owner review, no required review-thread resolution, and non-strict required status checks. This differs from the written governance rule requiring an independent approval.
- The connected Render account showed one live service, `JanaVani`, using `uvicorn src.web.canonical_app:app --host 0.0.0.0 --port $PORT`. Proposed `render.yaml` definitions for the separate WebApp and Telegram webhook are not proof of deployment.

## Priority release blockers

### P0.1 — Branch policy and retirement

- Correct the live ruleset so independent review matches the written governance policy.
- Do not merge PR #213 until independent review and the required checks are valid.
- Allow the guarded post-merge workflow to archive the exact transition-branch head, delete its ref, and verify the physical inventory is exactly eight.
- Re-query GitHub after deletion. Do not claim compliance from a green PR alone.
- Keep the eventual one-branch goal (`main` only) gated on full product-readiness evidence; archive useful work before retiring feature branches.

### P0.2 — Telegram inbox privacy/retention

The current `PostgresTelegramInbox.accept` stores the full Telegram update JSON in the durable inbox. A text update may contain raw citizen narrative and identifiers. The inbox payload is cleared after successful processing or terminal dead-lettering, but can remain during pending, processing, and retry states.

This means the Case table's metadata-only persistence rule does not by itself establish that citizen narrative never enters durable Janavani storage. Issue #219 tracks the decision.

Required response:
- define precisely which fields may be durably retained;
- define maximum retention and deletion behavior for success, retry, and dead-letter;
- review encryption/key management, least-privilege database access, logging and telemetry;
- cover text, captions, attachments, contact/location, and other structured updates;
- align the user-facing privacy notice with actual Telegram and Janavani processing;
- add PostgreSQL-backed negative tests proving prohibited fields do not persist, or prove the approved encrypted/TTL policy.

Do not silently centralize raw citizen content to obtain workflow continuity.

### P0.3 — Replay safety

Telegram delivery is at-least-once. Existing code has inbox deduplication and lease fencing, while durable Case/Submission repositories have idempotency mechanisms. These components do not alone prove that an already-committed business effect remains unique if a worker dies before marking the inbox row processed.

Issue #217 requires a real PostgreSQL test through the handler/capability path, failure injection after commit, replay through a fresh worker/repository, durable projection/version/event assertions, conflicting idempotency-key rejection, and eventual inbox completion.

Reuse the current durable transaction/idempotency boundaries; do not add a second generic idempotency framework.

### P0.4 — WebApp identity and independent deployment

The working branch describes an OIDC authorization-code flow with PKCE, state/nonce validation, JWKS validation, short-lived internal API assertions, secure cookie settings and a liveness route. The actual issuer/client/session configuration and end-to-end flow still need deployment evidence.

The currently observed Render inventory contains only the canonical API service. Deploy and test the WebApp, API, and Telegram webhook as independent runtimes before describing the end-to-end ecosystem as product-ready.

The current Web session is a signed stateless cookie with a bounded lifetime; logout clears the local cookie but cannot revoke a copied cookie server-side. Implement/test shared revocation or explicitly accept this bounded residual risk before product-ready release for sensitive citizen data.

### P0.5 — Reproducible build/type/lint gates

Issue #218 tracks:
- one authoritative Python dependency-lock strategy, compatible with the current deployment commands;
- a Cargo.lock decision appropriate to the repository's Rust workspace and application use;
- `cargo test --workspace --locked` alongside `cargo check` and Clippy;
- a Ruff baseline followed by required clean/changed-code gates;
- selective static type checking at high-risk boundaries (identity, domain/application contracts, repository interfaces).

Do not maintain competing lock sources or turn this into an unscoped legacy rewrite.

## Current architecture map

The source tree already contains the meaningful boundaries:

| Responsibility | Canonical path(s) | Responsibility and audit note |
|---|---|---|
| Canonical HTTP API composition | `src/web/canonical_app.py` | FastAPI app assembly, router registration and health/version routes. |
| HTTP surface adapters | `src/web/*_router.py` | Request parsing, identity dependency and HTTP response semantics; should not own domain rules. |
| Interactive WebApp | `src/webapp/main.py`, `src/webapp/*` | Presentation and request-scoped API client; separate runtime from API is intended and must be deployed/tested. |
| WebApp identity boundary | `src/webapp/*oidc*`, identity/session modules | Browser authentication/session trust boundary. Verify actual configured issuer and server-side revocation policy. |
| Telegram composition/handlers | `src/bot_telegram.py`, `src/commands/*`, `src/conversation/*` | Telegram transport, conversation state and handler orchestration. Raw narrative is currently transient in process memory except the durable webhook inbox payload. |
| Telegram webhook/inbox worker | `src/web/telegram_webhook_app.py`, `src/web/telegram_inbox_worker.py` | Durable ingress, update validation, claim/lease, retry and dispatch. Full-update persistence is the privacy issue in P0.2. |
| Shared Case capability | `src/capabilities/civic_case*`, `src/core/civic_case.py` | Case operations, domain types, lifecycle invariants and authorization. Keep cohesive. |
| Shared civic-action capabilities | `src/capabilities/civic_action*`, Authority/Evidence/Consent/Document/Submission modules | Reusable domain services used across surfaces. One canonical owner per capability. |
| Provider composition | `src/storage/provider_composition.py`, `src/platform/composition_*.py` | Resolve provider policy once and construct a consistent dependency graph. Keep provider-specific clients out of surfaces. |
| Persistence adapters | `src/storage/repositories/*` | PostgreSQL and other repository implementations behind contracts. Transaction ownership must stay explicit. |
| AI provider boundary | `src/ai/*` | Provider adapters, shared gateway and routing; non-AI workflow must not depend on model availability. |
| Rust workspace | `Cargo.toml`, `crates/janavani-core`, `crates/janavani-application` | Typed core/application foundations. Do not claim the deployed API runs on Rust; current Render service is Python/Uvicorn. |
| Contract/architecture tests | `tests/*` | Unit, contract, integration and negative-path tests. Integration evidence must prove PostgreSQL paths were executed and not skipped. |
| SQL migrations | `db/migrations/*` | Persistence schema/security evolution. Every migration requires forward/rollback and restore evidence appropriate to risk. |
| Deploy/CI | `.github/workflows/*`, `render.yaml`, Docker files | Execution and deployment policy. Workflow green does not mean a defined service is deployed. |

### What should not be split further

- Keep Case lifecycle rules and state transitions together where they preserve the same invariants.
- Keep Submission + Case mutation inside the existing atomic transaction boundary.
- Keep the Telegram conversation state machine cohesive; only split storage/retention when the trust or persistence contract actually differs.
- Keep API route registration in the composition root; do not create new universal orchestration wrappers.
- Keep domain contracts provider-neutral; PostgreSQL-specific logic remains in repository adapters.
- Do not split functions/classes solely to satisfy a line-count target. If the 180-line guard blocks cohesive code, review the guard exception on architectural grounds rather than manufacturing fragments.

## Runtime/language/toolchain operating model

| Concern | Janavani rule |
|---|---|
| Constants/config | Native constants and typed configuration at composition/runtime boundaries; secrets never in source. |
| Functions/objects/collections/operators | Use normal Python/Rust/JavaScript constructs. Keep business rules in shared capabilities, not in interface code. |
| Data types | Rust compile-time checks; Python annotations plus runtime request validation and selectively enforced static checks; JavaScript input validation at the browser boundary. |
| User and identity | Never trust client-provided principal/actor identifiers. The API verifies the signed assertion and enforces capability/ownership policy. Telegram identity only maps to a canonical principal after explicit verified pairing. |
| Rulebook | Source of truth, ecosystem charter, master architecture, capability registry, data/consent contracts and decision records. The enforcement layer is tests, runtime validation and repository policy—not a new universal rules engine. |
| Engine | Shared domain + application/capability functions. AI is optional/replacable assistance, not authority for identity, facts, consent or consequential action. |
| Runtime | Python FastAPI/Uvicorn API; separate WebApp and Telegram processes intended. Each requires independent health, configuration and failure tests. |
| Event loop | Async HTTP/Telegram work uses Python's async runtime; blocking repository calls must not block the event loop. Browser JavaScript has its own event loop. |
| Compiler/interpreter/JIT/transpiler | Cargo/rustc compile Rust; Python runs under its interpreter; JavaScript executes in the browser engine and may be JIT-optimized. No custom compiler/JIT/transpiler is needed. |
| Packages/build | `pyproject.toml` and `requirements.txt` for Python; `Cargo.toml` for Rust. Choose one reproducible Python lock approach and make Rust locking explicit. There is no reviewed root npm/package-lock pipeline at this baseline. |
| Verification | Syntax, tests, static analysis, Rust compilation/tests, PostgreSQL integration/RLS, backup/restore, Docker and deployment smoke checks. Record exact SHA and runtime evidence. |

## Documentation authority and file organization

The intended authority order is:

1. `NORTH_STAR.md` — purpose/outcomes.
2. Ecosystem Charter — scope and governing invariants.
3. `docs/CONSTITUTIONAL_GOVERNANCE.md` — civic/legal framing.
4. `docs/SOURCE_OF_TRUTH.md` — canonical architectural rules.
5. `docs/JANAVANI_MASTER_ARCHITECTURE.md` — architecture.
6. `docs/JANAVANI_PRODUCT_LANDSCAPE.md` — capabilities and surfaces.
7. `ROADMAP.md` — construction sequence.
8. `docs/MASTER_TASK_CHECKLIST.md` — tasks and verification status.
9. `docs/CAPABILITY_REGISTRY.md` — capability ownership/status.
10. `planning/` — active specifications/contracts.
11. `docs/architecture/`, `docs/operations/`, `docs/90-audits/` — design boundaries, runbooks and dated evidence.
12. `archive/` — historical/superseded items only; never current implementation guidance.

The repository already has this intended structure in its README, but older dated checklist sections contain conflicting branch counts and historic verification statements. Keep the record for provenance; add a dated current rebaseline that explicitly supersedes it rather than silently rewriting history.

### Proposed file organization (do not bulk-move files without import/runtime proof)

```
/
├── README.md
├── NORTH_STAR.md
├── ROADMAP.md
├── pyproject.toml
├── requirements.txt
├── Cargo.toml
├── .github/workflows/
├── src/
│   ├── web/                  # FastAPI/API composition and HTTP adapters
│   ├── webapp/               # interactive WebApp presentation/API client
│   ├── adapters/telegram/    # Telegram identity/transport adapters
│   ├── commands/             # Telegram-to-capability commands
│   ├── conversation/         # cohesive Telegram state machine
│   ├── capabilities/         # shared application capability contracts/behavior
│   ├── core/                 # domain objects/invariants
│   ├── identity/             # trust and identity linking
│   ├── access/               # authorization and consent enforcement
│   ├── storage/
│   │   ├── repositories/     # provider adapters
│   │   └── ...               # provider composition and transactions
│   ├── ai/                   # AI provider/gateway
│   └── documents/            # document generation and artifact policies
├── crates/
│   ├── janavani-core/
│   └── janavani-application/
├── db/migrations/
├── tests/
├── docs/
│   ├── architecture/
│   ├── operations/
│   └── 90-audits/
├── planning/
└── archive/
```

This is a responsibility map, not an instruction to rename established Python packages indiscriminately. Existing imports and deployed entry points must be verified before moving anything.

## Webstudio / static-site generator / Cloudflare deployment guidance

- Webstudio can be used as a visual design/export tool for the public website; it must not become the authority for Janavani business logic or authenticated Case state.
- Static HTML/CSS/JS is suitable for a public brochure/knowledge site when content and interactions do not require server-owned private state.
- The authenticated citizen workspace needs a trusted session and API boundary, so a static export alone is not the complete application runtime.
- Cloudflare Pages is suitable to evaluate for the public static site and branch/preview workflow. Workers may be considered for a specific dynamic edge requirement, but do not rewrite the current Python API simply to adopt another platform.
- Keep deployment provider configuration outside domain/capability contracts. Render/Vercel/Cloudflare are replaceable deployment adapters.
- Compare any SSG/Vercel starter by build output, runtime dependency, SSR/SSG boundary, preview isolation, headers/CSP, secrets and API integration before choosing it. Do not introduce Node/package tooling without a concrete product need.

## Ordered next two engineering actions

1. **Privacy decision and tests:** resolve full Telegram update payload persistence (Issue #219), then add a PostgreSQL-backed negative test for prohibited fields and retention/deletion behavior.
2. **Replay proof:** close Issue #217 using failure injection through the actual Telegram handler and shared Case/Submission transaction, followed by independent WebApp/API/Telegram runtime acceptance.

After those, correct branch ruleset and complete the archive-first transition to exactly eight branches, then resolve reproducible-lock/type-check gates, deploy independent services and complete the end-to-end runbook.

## Evidence standard

Do not mark a workstream COMPLETE because a file exists, a PR is mergeable, a workflow was green on an earlier SHA, or YAML describes a service. Every product-readiness claim must record implementation commit, applicable tests, security/privacy/failure results, actual service IDs and deployed commit SHAs, and a completed acceptance record.

## Code-level findings from the continued line inspection

### Finding A — OIDC callback exception handling

- **File:** src/webapp/identity_gateway.py
- **Finding:** The callback's exception tuple referenced InvalidToken, but the module imported only Fernet from cryptography.fernet. When an invalid/expired encrypted transaction cookie caused the callback to enter the exception handler, resolving that tuple could raise NameError instead of returning the intended safe sign-in error.
- **Correction committed on the existing review branch:** import InvalidToken from cryptography.fernet in commit 7bdf0c5b5ee076b087ae49d07ed64da7dc7d5a2e.
- **Verification:** existing OIDC state-mismatch regression exercises the exception path; new CI for the current head must complete before marking the fix verified.

### Finding B — Architecture guard failure

- **File:** src/webapp/main.py
- **Evidence:** Architecture Guard run 40169156119 on the pre-fix review head reported src/webapp/main.py:28: line length 237 > 200 and src/webapp/main.py:35: line length 227 > 200.
- **Correction committed on the existing review branch:** wrapped SessionMiddleware configuration and the signed-out landing response without moving responsibilities or changing behavior in commit d37f19c7e8d9a021f21eed49c9e5d2852e7b2092.
- **Verification:** current-head Architecture Guard must pass before this is marked complete.

### WebApp trust flow inspected

The current route assembly in src/webapp/main.py installs Starlette SessionMiddleware, registers the identity-gateway routes, and routes API access through client_for_request. The latter calls api_assertion_for_session, which mints a five-minute HMAC assertion from a verified session identity and a fixed citizen capability set. Keep this trust flow request-scoped: do not restore a process-wide identity assertion or accept a user-supplied principal. The session cookie is stateless and has a bounded lifetime; local logout cannot revoke a copied cookie server-side, so the documented revocation/residual-risk release gate remains open.

### Code review boundaries

The most important reviewed source paths are now cross-referenced in the responsibility table above. The high-risk review was targeted at API/WebApp identity, Telegram durable ingress/worker, Case capability/content separation, provider composition, durable Case/Submission repositories, tests and runtime manifests. A complete file-by-file release audit still requires execution of the whole test suite and current-head checks; this document does not imply every source line has been dynamically exercised.

## Supplied Web publishing projects — source-derived findings and recommendation

### Webstudio

Source reviewed: [webstudio-is/webstudio README](https://github.com/webstudio-is/webstudio/blob/main/README.md) and the [Webstudio documentation](https://docs.webstudio.is/).

The project describes itself as an open-source visual development platform with hosted and self-hosting options. Its README states that the core is licensed under **AGPL-3.0-or-later**, while the optional sdk-components-animation package is proprietary and governed by a separate EULA. This is a material licensing consideration before adopting, redistributing, modifying, or self-hosting components.

**Recommendation:** use Webstudio as an optional design/authoring/export tool for public, mostly static pages. Keep Janavani's canonical source-controlled content, SEO metadata, accessibility, routing and deployment configuration reviewable in Git. Do not make Webstudio the owner of citizen identity, consent, Case lifecycle, or private state. Review the license implications before adopting any code/package rather than treating “open source” as meaning every package has the same license.

### webstudio-is/ssg-vercel-test

Source reviewed: [repository README](https://github.com/webstudio-is/ssg-vercel-test/blob/main/README.md), [generated root HTML](https://github.com/webstudio-is/ssg-vercel-test/blob/main/index.html), [second route](https://github.com/webstudio-is/ssg-vercel-test/blob/main/another-page/index.html), and [Vercel configuration](https://github.com/webstudio-is/ssg-vercel-test/blob/main/vercel.json).

The README contains only the repository title. The inspected tree is primarily generated HTML and bundled assets; it has no package.json in the reviewed root and no build pipeline exposed by the inspected files. The generated output demonstrates a root page, a second path, generated CSS/JS assets and Vercel image optimization URLs. It also contains a placeholder Open Graph origin (https://url/) and a third-party placeholder image URL, so it should not be copied into a public production site without output validation.

**Recommendation:** treat this repository as a **static-export output/compatibility fixture**, not a maintained application starter or a replacement architecture. If using it for validation, inspect the generated route map, canonical/OG URLs, asset paths, image optimization dependencies and runtime assumptions.

### Cloudflare Pages / Workers

Sources reviewed: [Cloudflare Pages overview](https://developers.cloudflare.com/pages/), [Git integration](https://developers.cloudflare.com/pages/configuration/git-integration/) and [Pages Functions](https://developers.cloudflare.com/pages/functions/get-started/). These official pages were current/recently updated in October 2026 when checked.

The documentation describes Git-backed deploys and preview deployments for branches/pull requests, with Pages Functions available for server-side functionality. The Pages overview also says Workers supports most Pages use cases and is Cloudflare's primary platform for new full-stack applications.

**Recommendation:**
- **Public Janavani website:** Cloudflare Pages is a reasonable candidate if branch previews, static asset delivery and automatic deployment are useful. Existing GitHub Pages can remain until a concrete migration requirement is satisfied.
- **Authenticated WebApp:** keep its session/identity/API trust boundary explicit. A static export may serve presentation assets, but it is not a replacement for the authenticated server-side WebApp or canonical API.
- **Dynamic edge logic:** consider Pages Functions or Workers only for a concrete, bounded use case. Do not rewrite the existing Python FastAPI API just to match a hosting provider.
- **Deployment control:** verify output URLs, CSP/security headers, cache policy, form behavior, accessibility, mobile/reduced-motion behavior, preview isolation and API links before publishing. A successful static build is not a successful authenticated user journey.

## Additional functional finding — constitutional route now fails closed

At the initial inspection, the WebApp's /bill-review/{bill_code} page advertised document generation, while /dispatch-objection called JanavaniWebAPIClient.download_constitutional_objection(), which intentionally returned None. The form was therefore a user-visible dead end.

The current review branch now returns a no-store HTTP 503 from GET /bill-review/{bill_code}, explaining that source-verified legislative profiles are not yet available; POST /dispatch-objection returns HTTP 410 and explicitly states that no file was generated or transmitted. The prior user-facing intent and reactivation checklist are preserved in archive/documentation/legacy/2026-10-25-webapp-constitutional-bill-review-route.md. Regression tests were added to tests/test_webapp_runtime.py. The existing canonical API route is not enough to safely reactivate the workflow: the bill profile registry currently has no source-reference/provenance fields, and generation requires an owner-scoped objection Case plus a verified authority.

Issue #220 remains open until current-head CI verifies these fail-closed routes and future reactivation meets the archive note's source-provenance, authority, privacy, safe-header and end-to-end acceptance requirements. Do not re-enable the form merely because the API endpoint exists.

## Repository organization findings

The reviewed tree snapshot at commit 9d532b32ee23c68d68a7abe5857dfea21691be60 contained 1,121 tree entries (982 blobs): 582 .py, 52 .rs, 260 .md, and 9 .sql files across the full tree. Under src/, 298 Python/Rust source files were present. This is an inventory count, not an assertion that all those files are active runtime code; archive and legacy trees are deliberately included in the repository.

Repeated Markdown basenames were observed, including README files, CONTRIBUTING files, archived/current Privacy Architecture documents, and archived/current Developer Guides. Same basenames under different directories are not by themselves duplicates. Before consolidation, compare substance, links, import/deployment references and archival purpose. Preserve prior material under archive/ and update canonical links rather than deleting based on filename similarity.

**Current source of truth for this proof cycle:** this dated audit plus the superseding section in docs/MASTER_TASK_CHECKLIST.md. docs/README.md is the documentation entry point; root README.md points to this audit. Older dated audit/checklist statements remain historical evidence where they differ from the current rebaseline.



## Static public site and local-draft runtime distinction

- Root `index.html` is a public static landing page with an en-IN language declaration, canonical/OG/Twitter metadata, WebSite JSON-LD, the required “WE, THE PEOPLE OF INDIA” wording, a skip link, visible keyboard focus, responsive layout and reduced-motion handling. Keep this static source under Git control and test published routes/metadata before a hosting migration.
- `src/web/static/citizen-workspace.html` with `citizen-workspace.js` is deliberately local-only drafting: its CSP disables network connections (`connect-src 'none'`) and its text explains that drafts are not transmitted. The canonical API serves it at `/app`; it is not the authenticated server-backed Case workspace.
- `src/webapp/main.py` is the separate interactive WebApp with OIDC login/session, API client, Case/authority routes and Telegram pairing UI. It requires a separate service deployment and a trusted OIDC configuration. Do not blur the local-only draft page, public marketing site, and authenticated WebApp into one runtime.


## Vercel production deployment audit — live metadata check

**Audit checkpoint:** 25 October 2026. Read-only inspection using the connected Vercel deployment metadata, GitHub source at the identified production commit, and official Vercel runtime documentation. Detailed project settings, environment metadata, protected live content and runtime diagnostics remain blocked until the owning Vercel team authorizes this connection. Do not confuse a successful deployment state with a completed production acceptance test.

### Confirmed live metadata

- Project: `janavani`, Vercel project ID `prj_bN8y2S50yEJvbUrxMelPdLhg5gln`.
- Production aliases include `janavani.vercel.app`.
- Production deployment state: `READY`.
- Production git source: `main`, SHA `7bb10a881601c24e99f2deb1b98ce84266259ee8`.
- Development candidate PR #204 remains draft and unmerged; its head is a different commit. Candidate-ready metadata does not mean its OIDC or WebApp changes are in production.
- Vercel reports deployment type `LAMBDAS` and project framework metadata `flask`. This is a metadata observation, not proof of an application failure.

### Framework reconciliation — do not remove Flask blindly

At production SHA `7bb10a881601c24e99f2deb1b98ce84266259ee8`:

- `pyproject.toml` lists Flask before FastAPI in `[project].dependencies` and sets `[tool.vercel].entrypoint = "src.web.canonical_app:app"`.
- `requirements.txt` also lists Flask and FastAPI.
- `src/web/canonical_app.py` exports a FastAPI app and invokes `validate_runtime_configuration()` during application creation.
- `src/bot_whatsapp.py:12-14` and `src/bot_messenger.py:11-14` import Flask and create their own Flask apps for independent webhook surfaces. Flask is therefore not an unreferenced dependency that can safely be deleted from the ecosystem without a dependency/build redesign.
- No `vercel.json`, `vercel.ts`, or `.vercel/project.json` was present in the reviewed source tree.

Vercel's current documentation says FastAPI is supported, and custom application modules can be selected using `tool.vercel.entrypoint`. See [FastAPI on Vercel](https://vercel.com/docs/frameworks/backend/fastapi), [Python Runtime](https://vercel.com/docs/functions/runtimes/python), and [Project Configuration](https://vercel.com/docs/project-configuration).

**Decision:** do not delete Flask from common dependency manifests just to make Vercel auto-detection prefer FastAPI. That could break the independently intended WhatsApp/Messenger Flask entry points. After team access is granted, inspect the actual project framework/root/build/install settings, production env-variable names/targets (without disclosing values), exact deployment build events, and runtime errors. Then test the custom FastAPI entrypoint on a preview deployment. If the project has an explicit Flask preset, change that setting only after the preview proves the canonical FastAPI app starts and its required routes work; retain Flask in the dependency set until the messaging surfaces have a proper independently deployable dependency contract.

### Production runtime and configuration constraints

The canonical application invokes the production validator in `src/config/runtime.py`. In production the validator requires PostgreSQL providers for Case/artifact metadata/evidence/external identity links, S3 artifact blob storage, `JANAVANI_POSTGRES_DSN`, `JANAVANI_IDENTITY_LINKS_DSN`, and `JANAVANI_ARTIFACT_S3_BUCKET`. The source only proves these checks exist. The actual Vercel environment values/targets and whether the deployed runtime starts with `JANAVANI_RUNTIME_MODE=production` have not been verified due missing team authorization. Never retrieve, commit, or echo secret values for this audit; keys, targets and presence status are sufficient to start.

The canonical API is built around ASGI/FastAPI. The separate Telegram bot is a long-running process and should not be assumed to run as a normal request-scoped Vercel function without an explicitly designed webhook/worker adapter. Keep WebApp, API and Telegram as independently tested runtimes. Preserve truthful SOS delivery states: `not_submitted` and `police_delivery=not_implemented` must not be turned into a successful authority-delivery claim by a proxy HTTP success.

### Release/protection evidence

- Vercel deployment metadata establishes that production is on `main` at `7bb10a881601c24e99f2deb1b98ce84266259ee8`; it does not establish that the complete interactive WebApp/OIDC candidate has been promoted.
- The production SHA has check-run records, but check-run history is not equivalent to live runtime validation. A branch-budget check at that SHA failed on 11 October 2026 because it observed **10 physical refs** while the then-current gate expected nine; the extra `audit/2026-10-11-live-rebaseline` ref has since been retired. The current physical GitHub inventory is nine refs against the new target of eight.
- The current `main` ruleset (ID `25706799`) requires zero approving reviews, does not require Code Owner review, and does not require review-thread resolution, while the canonical repository policy specifies an independent approval. The active settings must be corrected by an authorized repository administrator; source documentation alone does not enforce it.
- The guarded PR #213 transition changes CI to an eight-ref policy and deletes its own temporary transition ref only after exact archive-head and tree checks. PR #213 CI at `d036839730968771e0db6d043eb2c85ad9531a88` passed its observed workflow groups, but the physical inventory remains nine and the ruleset mismatch blocks merge.

### Vercel inspection acceptance checklist

- [ ] Owner-team authorization completed; then re-fetch actual project settings.
- [ ] Verify framework preset, root directory, build/install commands, supported Python version, custom `tool.vercel.entrypoint`, and actual build output.
- [ ] Inspect production and preview environment-variable names, targets and presence without disclosing values; confirm production mode and all required durable providers.
- [ ] Inspect current production build events and runtime-error clusters.
- [ ] Exercise the public production alias, health/liveness and version routes if access permits; record HTTP statuses and returned service/version metadata.
- [ ] Build a preview from the selected FastAPI candidate and verify root, /liveness, /version, expected route registration, authentication/authorization boundaries, database readiness and failure behaviour.
- [ ] Test cookie expiry/revocation, CSRF/origin controls, cross-user ownership, restart/replay safety and truthful external-delivery statuses.
- [ ] Record exact source SHA, deployment ID, settings snapshot (no secret values), checks, smoke-test outputs and rollback target before any promotion.

**Interim verdict:** production metadata reports `READY`, but the Vercel deployment audit is still incomplete. No framework, routing, environment-variable, protection or production promotion change is authorized by this inspection note.
\n

## Vercel production risk audit reference

The focused companion audit is [2026-10-25-vercel-production-risk-audit.md](2026-10-25-vercel-production-risk-audit.md). It records the production deployment ID/SHA, the Flask/FastAPI configuration discrepancy, active Flask use by the WhatsApp/Messenger adapters, authorization errors, production-configuration validation requirements, and the safe read-only → preview-test → reconcile → verify sequence. Follow Issue #221 for closure.


## Telegram privacy disclosure correction — 25 October 2026

A targeted source review confirmed that the PostgreSQL inbox stores the full Telegram update JSON while work is pending, processing or retrying. The privacy command previously described issue text as process-local without explaining that the original webhook payload may also remain in the durable inbox. That disclosure was incomplete.

The current review branch now updates src/commands/privacy.py and src/commands/start.py to explain:
- webhook mode can retain the full update payload in the PostgreSQL inbox while pending/processing/retrying;
- payload is cleared on successful processing or terminal dead-lettering;
- the implementation does not enforce a wall-clock deletion deadline while the worker is offline;
- the 15-minute process-local workflow text buffer is separate from the durable webhook inbox;
- until retention is enforced, users should share only minimum necessary, non-sensitive details.

Regression tests were added to tests/test_telegram_privacy.py. This is a disclosure correction, **not closure of Issue #219**. The architectural decision and live-PostgreSQL test remain outstanding. Do not describe the current webhook path as local-only or fully privacy-verified.
