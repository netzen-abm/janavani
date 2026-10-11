# Janavani — Live Repository Audit and Master Rebaseline

**Audit date:** 11 October 2026  
**Repository:** [netzen-abm/janavani](https://github.com/netzen-abm/janavani)  
**Canonical branch at audit start:** `main`  
**Canonical main SHA observed:** `0fb4c50d188811bed700555e1ed82735adef790e`  
**Scope:** live branches, canonical source responsibilities, active-source line policy, CI/PR evidence, Web/Telegram status, GitHub Pages, GitHub automation.

## 1. Executive decision

The project is ready for a **proof-and-product cycle**, not another architecture-generation cycle. The current architecture already has a canonical FastAPI assembly, independent Telegram runtime, provider/capability composition, Case/lifecycle and submission boundaries, and PostgreSQL integration gates. The highest-value work is proving those pieces in deployment and finishing the first usable Web + Telegram civic-action journey.

The governing code split rule remains: split only when it establishes an independent boundary of change ownership, trust/security, persistence, provider dependency, independent reuse, lifecycle/state testability, or external transport. Keep orchestration and invariants together where splitting would duplicate decisions or weaken correctness.

## 2. Repository and source inventory

A recursive Git tree query of `main` returned 1,048 tree entries. Filtering active `src/`, `api/`, and `crates/` Python/Rust source paths (excluding archive and historical v2/v3 trees) found **292 source files: 269 Python and 23 Rust**.

The CI workflow runs `scripts/check_code_line_limits.py --limit 180`. The checker measures active `.py` and `.rs` files under `src/`, `api/`, and `crates/`; archived/historical code is excluded. The 11 October PR #204 CI head passed this gate. This means the tested PR head passed the mechanical ceiling; it is not a claim that every path in every old branch has been measured or tested.

### Representative active-file line counts on `main`

Line counts are the source file's actual text lines, excluding a trailing newline.

| File | Lines | Audit decision |
|---|---:|---|
| `src/web/canonical_app.py` | 55 | Retain as API assembly; not proof that deployment uses it correctly. |
| `src/bot_telegram.py` | 86 | Retain as independent bot bootstrap/composition boundary. |
| `src/capabilities/submission.py` | 138 | Retain as cohesive public capability façade; delivery/state/security flow has already been delegated to focused modules. |
| `src/capabilities/civic_action_vertical_slice.py` | 172 | Near the 180-line guard; do not split just to reduce lines. Split only on a real lifecycle/change boundary. |
| `src/capabilities/civic_case_impl.py` | 153 | Retain; canonical Case capability implementation. |
| `src/platform/surface_case_composition.py` | 180 | At the guard ceiling; avoid scope creep and re-measure after every change. Do not fragment composition without a real ownership boundary. |
| `src/storage/repositories/postgres_policy.py` | 157 | Retain as provider/persistence boundary; scrutinize transaction and authorization behavior in tests. |
| `src/core/case_model.py` | 108 | Retain as cohesive domain model. |
| `src/webapp/main.py` | 135 | Keep as Web interface composition; verify that its actual routes and behavior agree with the intended canonical experience. |
| `scripts/check_code_line_limits.py` | 52 | Retain as CI maintainability guard. |

The full guard is the line-count authority for active Python/Rust source in CI. The representative table is a short audit sample, **not** a replacement for the script's automated check.

## 3. Canonical architecture and key files

Current ownership verified from `docs/ARCHITECTURE.md` and implementation files:

- `src/web/canonical_app.py` assembles the FastAPI API routers.
- `src/bot_telegram.py` builds the Telegram application separately and calls shared Case composition.
- `src/platform/surface_case_composition.py` composes shared Case/Evidence/Authority/Consent capabilities for surfaces.
- `src/capabilities/civic_action_vertical_slice.py` coordinates the existing civic-action capabilities.
- `src/capabilities/submission.py` is the submission façade; submission flow/security/state have their own focused modules.
- `src/storage/repositories/` holds persistence adapters and provider-specific transaction code.
- `render.yaml` defines separate service entries: Web/API starts with `uvicorn src.web.canonical_app:app`; Telegram starts with `python src/bot_telegram.py`. The Web/API entry now declares `healthCheckPath: /liveness` in this audit branch; this endpoint exists in `src/web/canonical_app.py`. This is the desired manifest configuration, but **the file alone is not deployment proof**.
- **Live Render inspection (11 October):** the connected Render workspace currently lists only one service for this repository: `JanaVani` at `https://janavani-bot.onrender.com`, type `web_service`, tracking `main`, start command `uvicorn src.web.canonical_app:app --host 0.0.0.0 --port $PORT`, and `healthCheckPath` empty. No separate Telegram Worker appeared in the service inventory. Its most recent observed deploy of main SHA `0fb4c50d188811bed700555e1ed82735adef790e` succeeded on 10 October, with a `GET /` 200 log, but the live /liveness probe and a Telegram process were not observed. Therefore **API deploy succeeded; Telegram deployed independence is not established**. The manifest's health check path change is on the current review branch and will not alter the live service until merged/applied.

No arbitrary class/file splitting is recommended during the next cycle. Focus on reproductions, failure cases, and observed behavior.

## 4. Live branches — hygiene incident and recovery

The approved branch set remains the nine branch roles listed in `docs/MASTER_TASK_CHECKLIST.md`. However, the live branch query after this audit's checklist edit returned **10 physical branches**, because the audit process created an additional branch, `audit/2026-10-11-live-rebaseline`. This was an execution error against the exact-nine rule; the repository must not be reported as currently satisfying that rule.

The extra branch points to the checklist rebaseline commit `57a2d0cf237dae0a4002a08d45e0fd16e9143246`. Its checklist content has been re-applied to the sanctioned branch `chore/ecosystem-shared-capability-infrastructure`, so that branch can be the durable review vehicle. No other branch is authorized or should be created.

**Recovery procedure:** run the existing [Branch Retirement workflow](https://github.com/netzen-abm/janavani/actions/workflows/branch-retirement.yml) from the `main` ref, set `execute=true`, and enter the exact confirmation phrase `RETIRE-LEGACY-BRANCHES`. Review the run output before/after; the workflow tags the non-sanctioned branch head under `archive/branches/...` before deleting its branch ref and is designed to finish at nine refs. Then re-query the live branch list and confirm exactly nine. The connected GitHub actions available in this session do not expose branch deletion or workflow dispatch, so I could not execute that cleanup here. Until the workflow succeeds, the exact-nine requirement remains **BLOCKED**.

Do not merge or delete any of the nine sanctioned branches merely to achieve a count; they are already the approved set. Do not wholesale-merge `integration/canonical-platform`: PR #203 is a review/convergence vehicle and is divergent from main.

## 5. CI and pull-request findings

### PR #204 — secure identity pairing and citizen workspace

PR #204 is open and **draft**. Its head `6ff2f2788ead52ee08943b97887f83f2d913a796` passed the observed CI, Docker, Architecture Guard, Security CI, and Dependency Review runs on 11 October before later audit commits. Its test job reported success for:
- Python syntax and active-source line limit;
- smoke tests;
- canonical Web vertical-slice tests;
- Web/Telegram shared-capability tests;
- canonical test suite;
- live PostgreSQL RLS isolation;
- PostgreSQL identity-pairing tests;
- backup/restore integrity;
- PostgreSQL restart durability.

These are **PR-head CI results**, not proof that the same code is merged or deployed. Fresh checks are required after the audit/configuration commits.

#### CodeQL configuration finding — corrected

The initial review flagged removal of the advanced CodeQL job as a possible security regression. I then re-added that job briefly and inspected its failure logs. The exact failure was: **`CodeQL analyses from advanced configurations cannot be processed when the default setup is enabled`** (run [38123086974](https://github.com/netzen-abm/janavani/actions/runs/38123086974), failed CodeQL Analyze job).

Therefore, the correct solution is **one CodeQL configuration mode, not running advanced setup alongside GitHub's enabled default setup**. The conflicting advanced CodeQL job has been removed again in commit `b04a2c538f0936d26b6f7ba3d70742a1d41a53f0`. A correction was posted on [PR #204](https://github.com/netzen-abm/janavani/pull/204#issuecomment-6106911394); it supersedes my earlier premature request to restore the advanced job. Remaining gate: verify that the default CodeQL setup is actively completing current analyses and that fresh Security CI passes. A green custom Security CI run alone is not proof of default CodeQL coverage.

Other required gates before merge/release:
- verify the trusted identity gateway that issues signed, short-lived assertions; never trust browser-supplied principal IDs;
- confirm Web and Telegram use the same identity database/schema with a dedicated least-privilege role and consistent secret/configuration;
- independently audit protected-data authorization and cross-user denial paths;
- prove pairing replay/concurrency/link reassignment behavior against PostgreSQL;
- verify the intended API runtime and independent Telegram worker in the actual deployment environment.

The `/app` addition is deliberately a local drafting workspace: draft, preview, download and print. It does not yet represent a complete Case-persistence, submission and tracking journey. Do not describe it as the full production WebApp.

### PR #203 — canonical platform convergence

PR #203 remains open/unmerged and should not be merged wholesale. It calls for PostgreSQL cross-user authorization/RLS, restart/recovery, backup/restore, canonical Web/API runtime, and independent Telegram runtime evidence. Compare/extract only still-missing changes proven compatible with current main contracts.

## 6. Product proof gates and next order

### P0 — runtime truth and security/persistence proof
1. Clean the extra branch and re-verify nine physical refs.
2. Verify that GitHub's enabled default CodeQL setup is actively completing analyses. Do not run the conflicting advanced CodeQL job at the same time; re-run custom Security CI after configuration de-duplication.
3. Verify Web/API and Telegram startup, health, provider configuration and failure independence in deployed environments.
4. Run deployment-equivalent PostgreSQL cross-user/RLS denial, least-privilege role, migration/rollback, transaction atomicity, restart/outage/recovery and backup/restore checks.
5. Verify identity/consent expiry and revocation, data redaction, sensitive-content persistence boundary, ephemeral document/artifact handling and honest delivery states.

### P1 — one complete Web + Telegram civic-action journey
Verify the same shared capabilities end-to-end:
`issue → Case → authority → evidence reference → document → review/correction → explicit consent → submission preparation → acknowledgement/tracking → follow-up/outcome`.

The WebApp and Telegram must share domain/capability logic while keeping independent runtime/process failure boundaries. Cross-surface Case continuation only becomes a verified feature after identity, authorization and durable storage are proven together. Document generation is not submission; an attempted transmission is not an acknowledgement.

### P2 — expansion
Only after P0/P1 gates: Mini App, WhatsApp/Messenger, Android/iOS, broader AI/RAG/Agentic AI, DApp/Web3, and resilient/mesh/satellite transports. The staged sequence does not reduce the full ecosystem scope.

## 7. GitHub Pages recommendation — live site-source audit

**Important correction:** the link `https://netzen-abm.github.io/janavani/` is not the canonical public brochure-site URL reported by the website repository's current successful Pages deployment. The dedicated `netzen-abm/janavani-website` repository explicitly identifies `https://netzen-abm.github.io/janavani-website/` as its canonical public URL. The platform repository `netzen-abm/janavani` has its repository homepage metadata set to the old `/janavani/` URL; that setting is stale relative to the current brochure deployment.

Live website-repository checks:
- Main SHA: `4d2ca7c45ba80bb786a9ec46cf7f1876dba0e0df`.
- GitHub Pages workflow run [38120947149](https://github.com/netzen-abm/janavani-website/actions/runs/38120947149) completed successfully on 11 October 2026.
- The workflow stages an explicit allowlist of public HTML, CSS, JavaScript, icons and referenced images, then validates metadata, local references, encoding, sitemap, manifest and artifact scope before deploying.
- Six production HTML pages were inspected: each has one H1, a title, description, canonical URL, Open Graph/Twitter metadata and one JSON-LD block; no missing `alt` attributes were detected in the quick markup scan.
- The homepage H1 visibly encodes **“WE, THE PEOPLE OF INDIA”** across three spans. Pages share the lightweight SVG favicon, Apple touch icon, manifest and sitemap/robots support.
- The website repository's own progress record estimates the validated deployment artifact at about 1.03 MB, substantially narrower than the prior broad asset-copy approach.
- A reliable rendered/browser inspection was not available in this session (the web viewer could not fetch the URLs), so responsive visual QA, keyboard/navigation QA and actual device testing remain open despite the successful build/deploy validation.

**Recommendation / corrective action:** make `https://netzen-abm.github.io/janavani-website/` the canonical public website URL everywhere. Update the **platform repository's Settings → General → Website** field from the stale `/janavani/` URL to the canonical `/janavani-website/` URL, and update any public README links when the main branch can be safely changed. If backward compatibility for `/janavani/` is required, make it a deliberate minimal redirect/landing page after confirming that repository's Settings → Pages publishing source; do not create a second copy of the brochure website.

Keep the two responsibilities separate:
1. **`janavani-website` + GitHub Pages:** public information, SEO/AEO, civic explainers, resources, FAQs and other safe static content.
2. **`janavani` platform:** authenticated/dynamic WebApp, canonical API, PostgreSQL and independent Telegram runtime. GitHub Pages cannot replace the API, database or Telegram worker, and static JavaScript must contain no secrets.

Official guidance: [GitHub Pages quickstart](https://docs.github.com/en/pages/quickstart), [publishing-source configuration](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site), and [custom Pages workflows](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages).


## 8. GitHub App / GitHub Actions recommendation

Use **GitHub Actions first** for repository-local CI, branch-budget enforcement, security scans, Pages build/deploy, and release evidence. Consider a **GitHub App** only when Janavani needs a persistent integration that responds to webhooks or safely operates across repositories/installations. Prefer repository-limited installations, minimum read/write permissions, short-lived installation tokens, signed/verified webhooks, least-privilege secret storage, auditable actions, and explicit approval for destructive actions. Do not give an automation App broad Administration permissions merely for convenience.

Official guidance: [GitHub Apps best practices](https://docs.github.com/en/apps/creating-github-apps/about-creating-github-apps/best-practices-for-creating-a-github-app) and [deciding when to build a GitHub App](https://docs.github.com/en/apps/creating-github-apps/about-creating-github-apps/deciding-when-to-build-a-github-app).

## 9. Completion definitions

- **Implemented:** source exists.
- **Tested:** named tests passed against an identified commit.
- **Runtime-verified:** behavior observed in its deployed runtime.
- **Production-verified:** runtime, identity/authorization, privacy/security, persistence/recovery and deployment gates have linked evidence.

A green test workflow is strong evidence, but not a substitute for deployment validation.
