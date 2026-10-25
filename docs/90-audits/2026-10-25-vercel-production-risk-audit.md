# Janavani — Vercel Production Deployment Risk Audit

**Audit date:** 25 October 2026  
**Repository:** [netzen-abm/janavani](https://github.com/netzen-abm/janavani)  
**Production URL:** [janavani.vercel.app](https://janavani.vercel.app/)  
**Production deployment:** dpl_97pqeadaZULDUfXtKkagepkP49Z5  
**Production source:** main / 7bb10a881601c24e99f2deb1b98ce84266259ee8  
**Audit mode:** Read-only; source and deployment metadata inspected. Detailed Vercel project settings, environment metadata, protected endpoint checks and runtime diagnostics remain blocked pending team authorization.

## 1. Executive assessment

Vercel reports the production deployment as READY, but this state alone does not establish that the correct application, secure environment, durable persistence, identity settings and supported citizen journeys operate correctly together.

The confirmed production deployment is from main at 7bb10a881601c24e99f2deb1b98ce84266259ee8. PR #204 is still a draft and unmerged. Its OIDC/WebApp changes must not be described as running in production.

The live project metadata reports framework flask, while the canonical application is FastAPI at src.web.canonical_app:app. This is a **configuration discrepancy requiring investigation**, not proof that production is broken.

**Interim verdict: operationally deployed, but production readiness is not established by the evidence currently available.** No Vercel settings, aliases, environment variables or production traffic have been changed as part of this audit.

## 2. Findings verified from Vercel/GitHub metadata

| Area | Observed evidence | Assessment |
|---|---|---|
| Production deployment | Vercel deployment is READY; alias list includes janavani.vercel.app. | Availability metadata only, not end-to-end acceptance. |
| Production version | Production is main at SHA 7bb10a881601c24e99f2deb1b98ce84266259ee8. | Candidate changes remain separate until merged/deployed. |
| Candidate status | PR #204 is open, draft, and not merged. | Do not promote on the basis of preview success alone. |
| Framework | Vercel metadata says flask; repository entry point is FastAPI. | Inspect actual framework/root/build/runtime settings and build logs before deciding whether to change anything. |
| Project access | Access to the owning Vercel team/project environment and deployment events returns 403. | Configuration/log audit incomplete until access is authorized. |
| Vercel config file | No vercel.json, vercel.ts, or .vercel/project.json was found in the reviewed repository tree. | Absence of a repo config does not reveal the dashboard's actual project settings. |
| Branch inventory | GitHub reports nine physical branches, including eight intended active roles plus the retirement-only transition branch. | Target of eight is not yet achieved. |

The team-access authorization request was generated for owner/team scope team_Y4Eko8RPDrCfo4oKU522O0my. At the latest check, project settings, environment metadata and deployment event/log calls still returned 403. The authorization link itself is time-limited and may expire; generate a fresh consent request when continuing the inspection rather than bypassing authorization.

## 3. Framework and dependency findings

### Canonical API entry point

At the reviewed production SHA:

- pyproject.toml declares [tool.vercel].entrypoint = "src.web.canonical_app:app".
- requirements.txt and pyproject.toml include Flask and FastAPI.
- src/web/canonical_app.py creates and exports the canonical FastAPI app and calls validate_runtime_configuration() during application creation.
- Dockerfile and Procfile also identify src.web.canonical_app:app as the FastAPI/Uvicorn API entry point.

### Flask is still used by independent access-surface code

The current production tree uses Flask in:

- src/bot_whatsapp.py — Flask app/webhook adapter.
- src/bot_messenger.py — Flask app/webhook adapter.

These two adapters currently contain minimal webhook behavior and do not constitute full, production-verified citizen journeys, but they do show that Flask is not simply an unused dependency. Removing Flask from the shared manifest just to change Vercel framework auto-detection may break other declared surfaces.

### Recommendation

Do **not** remove Flask or change the live Vercel framework setting solely because the metadata says flask. First inspect the actual Vercel settings/build events and test a preview pinned to the intended FastAPI entry point. Change settings only after that preview proves startup and the expected API routes. Longer term, define clean dependency manifests per independently deployed runtime if the verified build/deployment boundary justifies it; do not introduce a packaging split purely for appearance.

Official Vercel references for the review:
- [FastAPI on Vercel](https://vercel.com/docs/frameworks/backend/fastapi)
- [Python Runtime](https://vercel.com/docs/functions/runtimes/python)
- [Project Configuration](https://vercel.com/docs/project-configuration)

## 4. Production runtime configuration and durable storage

The source validator at src/config/runtime.py fails closed for JANAVANI_RUNTIME_MODE=production unless the configured durable providers and required settings exist. The current code requires PostgreSQL providers for Case, artifact metadata, evidence and external identity links; S3 artifact blob storage; JANAVANI_POSTGRES_DSN; JANAVANI_IDENTITY_LINKS_DSN; and JANAVANI_ARTIFACT_S3_BUCKET.

This verifies that a source-level guard exists. It does **not** verify that the deployed Vercel environment selects production mode or contains correct target-scoped values. The actual environment configuration remains blocked behind the team-access authorization.

Required checks must examine variable names, targets and presence status without revealing or logging secret values. Confirm that missing mandatory production configuration prevents startup. Do not silently run with process-local persistence.

## 5. Identity, consequential-operation and failure-isolation risks

### WebApp session revocation

PR #204's OIDC candidate documents a 30-minute stateless signed Web session. Clearing the browser cookie on logout does not revoke a copied cookie server-side. This has not been independently tested against the deployed Vercel app.

Before sensitive citizen records are product-ready, either implement and test server-side revocation with bounded expiry or explicitly exclude the affected sensitive workflows pending a documented security decision. Verify OIDC issuer/client configuration, PKCE/state/nonce, audience/issuer/expiry/signature checks, same-origin/CSRF controls, ownership checks, expiry and replay.

### SOS / emergency delivery

The current source has explicit truthful statuses including not_submitted and police_delivery: not_implemented. Preserve these states until a provider integration is implemented and proven. A successful HTTP response must not imply that police, emergency services or another public authority received a message.

### Independent runtimes

The observed connected Render inventory contained a single live JanaVani service running uvicorn src.web.canonical_app:app from main at 7bb10a881601c24e99f2deb1b98ce84266259ee8. This separate platform account inventory is not evidence of the Vercel runtime. Proposed Render definitions for WebApp and Telegram are configuration, not proof of live deployment.

Prove WebApp, Web/API and Telegram independently: deployment commit, health/liveness, identity configuration, database/provider connectivity, restart/recovery, retries, ownership isolation, and the failure of one channel not disabling another.

## 6. Dependency reproducibility

At the reviewed source SHA, the dependency manifests use minimum-version ranges such as FastAPI>=0.115.0 and uvicorn>=0.30.0. A separate checked-in uv.lock or Cargo.lock was not present on the inspected review branch at the time of inspection.

Introduce one authoritative lock strategy compatible with current deploy commands; use the same resolved dependencies in CI and deployment, with reviewed upgrades and hash verification where supported. Do not maintain parallel lock sources without a clear owner.

## 7. Branch governance and release protection

Live GitHub inventory: nine physical refs. The intended policy is eight active roles; feat/canonical-capability-execution-envelope is the temporary retirement-only ref.

The current live main ruleset reports:
- required_approving_review_count: 0
- require_code_owner_review: false
- required_review_thread_resolution: false
- strict_required_status_checks_policy: false

This conflicts with the repository policy requiring an independent approval. The actual settings must be corrected by an authorized repository administrator. Documentation or a CI workflow does not itself enforce repository settings.

PR #213 contains the controlled eight-branch transition and archive-before-delete workflow. Its observed workflow groups passed at commit d036839730968771e0db6d043eb2c85ad9531a88, but the current physical inventory remains nine and no independent approving review has been recorded. Do not merge until the actual ruleset is reconciled, an independent approval is obtained, and applicable checks pass.

## 8. Ordered remediation and acceptance criteria

### Phase A — finish read-only Vercel inspection
- [ ] Authorize the correct project-owning team.
- [ ] Fetch actual project framework, root directory, build/install commands and Python runtime settings.
- [ ] Fetch environment-variable names/targets/presence without exposing values.
- [ ] Inspect deployment build events and runtime error clusters.
- [ ] Check access to the production alias and exact status/body of root, liveness and version routes using an authorized path.

### Phase B — reconcile runtime safely
- [ ] Verify custom FastAPI entry point and route handling from a preview deployment.
- [ ] Verify startup fails if required durable providers or identity configuration are missing.
- [ ] Keep Flask for the surfaces that use it unless the runtime packaging is deliberately separated and regression-tested.
- [ ] Record preview deployment ID, exact source SHA, build output and smoke-test results before any production setting change.

### Phase C — prove security and citizen journeys
- [ ] Verify OIDC and session revocation/expiry/CSRF behavior.
- [ ] Verify cross-citizen Case/document/evidence isolation.
- [ ] Prove PostgreSQL-backed Telegram inbox privacy and post-commit replay safety.
- [ ] Verify truthful submission/SOS state and no unsupported external-delivery claim.
- [ ] Prove WebApp, API and Telegram startup/recovery/failure isolation independently.

### Phase D — controlled release
- [ ] Correct the actual GitHub main ruleset and obtain independent review for PR #213.
- [ ] Complete its controlled archive/tag/delete transition and verify exactly eight physical refs after deletion.
- [ ] Complete reproducible dependency locking and exact-head CI/security checks.
- [ ] Record production deployment SHA, environment review (no secrets), smoke tests and a tested rollback target.
- [ ] Keep PR #204 in draft until all applicable acceptance gates pass.

## 9. Final verdict

Vercel reports the current production deployment as READY, but the available metadata does not establish complete production readiness. The exact production SHA, FastAPI code entry point, framework-preset discrepancy, actual production environment, session/revocation risks and separate runtime guarantees have been recorded.

The correct next move is **inspect → preview-test → reconcile → verify → promote**, not blind configuration changes. No production configuration, environment variable, alias or deployment was changed during this audit.
