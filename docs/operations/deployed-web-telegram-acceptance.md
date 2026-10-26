# Deployed Web–Telegram Acceptance Runbook

**Status:** Release gate; not evidence that production acceptance has passed.  
**Scope:** Verify the existing Web/API and Telegram webhook as independent processes sharing canonical identity and Case state.  
**Rule:** Run first in a disposable/staging environment. Never use real citizen records or paste secrets into logs, tickets, shell history, or browser-visible output.

## Release preconditions

- [ ] The intended physical branch target is exactly eight sanctioned refs.
- [ ] Before release acceptance, PR #213 retirement has completed and a fresh GitHub branch query confirms exactly eight refs; a green PR alone does not establish physical compliance.
- [ ] Candidate commit and all required CI/security/architecture/Docker/dependency checks are green.
- [ ] Web/API and Telegram webhook are independently deployed and their actual service IDs, commit SHAs, URLs and health state are recorded.
- [ ] Both processes use the same approved PostgreSQL schema for canonical Cases and verified external identity links. Use separate least-privilege runtime roles where tables/capabilities differ.
- [ ] `JANAVANI_WEB_API_URL` is configured as HTTPS to the actual canonical API service.
- [ ] Production provider configuration passes `validate_runtime_configuration()`; no process-local fallback is used for durable Case, artifact, evidence, consent, submission, authority-directory or identity-link state.
- [ ] `JANAVANI_AUTHORITY_REPOSITORY_PROVIDER=postgres` is configured in production. The shared directory is seeded with source-backed records, and only records explicitly marked verified with a usable destination are offered to citizens.
- [ ] Artifact storage, citizen-content retention/deletion policy, migration state, backup/restore and operational alerting are approved.
- [ ] Apply `db/migrations/20261025120000_telegram_inbox_encrypted_payloads.sql` before deploying the encrypted queue implementation. Configure `JANAVANI_TELEGRAM_INBOX_ENCRYPTION_KEYS` as a secret (active Fernet key first, previous keys retained for decryption/rollback); the webhook must fail closed if it is missing or invalid. The production runtime must not reuse the deterministic CI key. Do not roll back to old raw-payload code; use a forward-compatible recovery build.
- [ ] After startup migration, inspect `SELECT count(*) FROM public.telegram_update_inbox WHERE payload IS NOT NULL`; it must be zero. Confirm pending work has `encrypted_payload IS NOT NULL`, a future `payload_expires_at`, and no plaintext marker in the ciphertext. Do not close privacy acceptance until legacy plaintext conversion and expired-row cleanup are verified.
- [ ] The WebApp uses a trusted OIDC issuer/client and HTTPS callback; authorization-code PKCE (S256), state, nonce, JWKS signature, issuer, audience and expiry validation pass. Client/session secrets exist only in server-side deployment secrets.
- [ ] Web sessions use HttpOnly, SameSite=Lax cookies and Secure cookies in production; the encrypted OIDC transaction cookie is short-lived. API assertions are freshly minted for five minutes and independently verified; the browser cannot choose a principal or capability list.
- [ ] Telegram webhook secret is configured in the provider and service; webhook URL is HTTPS and points to the actual deployed Telegram service.

- [ ] **Session revocation risk is explicitly accepted or closed.** The current Web session is a signed, stateless cookie with a 30-minute maximum age. Logout clears this browser cookie but cannot revoke a copied cookie server-side. Before product-ready release for sensitive citizen records, implement and test shared server-side revocation or record an explicit security decision accepting this bounded residual-validity risk.

## Test identities and data

Create two synthetic citizens, **A** and **B**, and one non-sensitive test Case owned by A. Use unique run IDs. Do not place personal or confidential information in fixtures. Record Case ID, synthetic principal IDs, deployment commit SHA and timestamps—not tokens or secrets.

## Acceptance sequence

### 1. Service inventory and health
- [ ] Confirm the Web/API and Telegram webhook are two independently managed deployed services.
- [ ] Record each service's deployed commit SHA and verify it matches the intended candidate.
- [ ] Request each configured liveness endpoint; both return healthy responses.
- [ ] Confirm Telegram webhook registration points to the deployed HTTPS URL. Verify registration through the trusted Bot API/operations path without logging the bot token.
- [ ] Verify the webhook rejects a missing or incorrect Telegram secret with HTTP 403.
- [ ] Verify oversized and malformed updates are rejected without worker dispatch.

**Pass:** Actual deployed services and commit SHAs are recorded; health and webhook registration are verified. A YAML declaration alone does not pass this gate.

### 2. Pairing and identity binding
- [ ] Citizen A authenticates through the approved Web identity gateway and requests a pairing challenge.
- [ ] Confirm the challenge is short-lived, non-cacheable, single-use and only its digest is persisted.
- [ ] A claims it through a private Telegram chat; claim alone does not create a verified link.
- [ ] The same authenticated Web principal explicitly confirms the pairing.
- [ ] A fresh Web/API process and the independent Telegram process both resolve the same canonical principal.
- [ ] Expired, replayed, mismatched-principal and conflicting-link attempts fail closed.
- [ ] Citizen B cannot claim A's pairing or reassign A's Telegram identity.

**Pass:** Identity binding survives process restart and cannot be transferred or replayed.

### 3. Web → Telegram Case continuity
- [ ] A creates/submits a test Case using an authenticated server-side workflow.
- [ ] Record the returned canonical Case ID and status.
- [ ] A's paired Telegram account retrieves that same Case and status.
- [ ] Compare persisted Case identity, owner, status and lifecycle event count through authorized read paths.
- [ ] B attempts to retrieve A's Case; access is denied without revealing protected Case details.

**Pass:** Both surfaces resolve the same durable Case and authorization remains principal-scoped.

### 4. Telegram → Web Case continuity
- [ ] A creates a test Case through the Telegram workflow.
- [ ] A retrieves the same Case through the authenticated Web workflow.
- [ ] Verify owner, Case ID, status and lifecycle events agree; neither adapter maintains a separate authoritative Case state.

**Pass:** Both directions use canonical persistence and consistent domain rules.

### 5. Delivery, idempotency and worker recovery
- [ ] Submit the same synthetic Telegram `update_id` twice; encrypted enqueue deduplicates it without double-accepting work.
- [ ] Inspect the database row during processing: `payload IS NULL`, `encrypted_payload IS NOT NULL`, and plaintext narrative markers do not appear in ciphertext bytes.
- [ ] Simulate a transient database outage in staging; encrypted enqueue fails retryably (HTTP 503) rather than acknowledging unpersisted work.
- [ ] Simulate handler failure; the webhook has already acknowledged durable queue acceptance, so the worker retains ciphertext, records the error class only, and retries with bounded backoff.
- [ ] Inject a process crash after the business transaction commits but before `mark_processed`; reclaim the same encrypted update and prove no duplicate Case/Submission mutation or lifecycle event.
- [ ] Repeat at a later conversation state with a fresh Telegram application process: session metadata and narrative are currently process-local, so verify the replay either restores only approved minimal metadata or fails closed with explicit restart/recovery guidance. It must not treat an old office/consent/format response as new issue text, create an orphan/duplicate Case, or claim a workflow completed.
- [ ] Verify expiry: after the 24-hour deadline, the worker dead-letters and clears expired payloads; document that physical cleanup runs when the worker is active and can be delayed by worker outage.
- [ ] If legacy payload rows exist, verify startup encrypts them before webhook registration and that `payload IS NOT NULL` reaches zero.
- [ ] Run concurrent workers and verify stale lease holders cannot commit after their claim has been fenced.
- [ ] Replay an update that would trigger a consequential action; prove the domain operation has its own idempotency guard. Inbox deduplication alone is not enough.
- [ ] Verify retry limits, dead-letter visibility, payload cleanup/retention and alerting.

**Pass:** New requests store no plaintext payload, durable acceptance succeeds only after ciphertext commit, worker retries/dead-letters within a bounded expiry, stale leases are fenced, and real-handler replay cannot duplicate consequential business effects. Workflow-state restart recovery or its explicit fail-closed alternative must also pass. Do not call the replay gate passed until the injected post-commit failure test succeeds against PostgreSQL.

### 6. Persistence and restart
- [ ] Restart the Web/API process and retrieve A's Case from a new session.
- [ ] Restart the Telegram process/worker and retrieve the same Case through Telegram.
- [ ] Verify identity links, Case state and lifecycle events persist.
- [ ] In staging, restore the approved backup into a disposable database and verify schema, RLS policies, constraints and synthetic records.

**Pass:** State survives process restart and documented restore validation.

### 7. Privacy and consent
- [ ] Camera, microphone, location and contacts are not requested for workflows that do not need them.
- [ ] If an optional capability needs a device permission, explain the purpose before requesting it and request only when the user initiates that capability.
- [ ] Verify permission denial does not break unrelated workflows.
- [ ] Verify the application does not continue collecting after the relevant action finishes; future use requires a fresh permission decision where the platform/API supports it.
- [ ] Verify consent withdrawal is persisted and enforced on subsequent reads/writes.
- [ ] Verify logs and errors do not expose pairing codes, identity assertions, tokens, raw evidence or unnecessary personal data.

**Pass:** Permissions and collection are purpose-bound, optional, revocable and observable in tests.

## Evidence record

For each test, record: test ID, environment, commit SHA, service IDs, timestamp, expected result, observed result, redacted log/query reference and pass/fail. Do not include secrets or real citizen data.

Release status must be one of:
- **PASS:** every mandatory gate above has evidence.
- **BLOCKED:** a required service, provider, permission, migration, or test fixture is unavailable.
- **FAIL:** an expected security, durability, consistency, or recovery invariant is violated.

Do not describe a CI-only result as a deployed acceptance pass. Keep the release PR draft until the mandatory gates pass and the evidence record is reviewed.

## Evidence update — 26 October 2026

**Current disposition: BLOCKED for production acceptance.** This update records CI and read-only environment evidence; it does not claim that the candidate was promoted to production.

### Verified code/test evidence

- Latest verified code/test head: `66d365e98aceaef1d672fd33e68cc7529a711040` (including the Telegram replay, pairing privilege hardening, and authority schema migration changes).
- CI run: `40332487893` completed successfully.
- Canonical Python suite on the current authority-schema candidate: **756 passed, 2 warnings** (GitHub Actions run `40335203888`, verified head `66d365e98aceaef1d672fd33e68cc7529a711040`).
- `tests/test_postgres_telegram_handler_replay.py::test_telegram_case_handler_post_commit_crash_replay_is_safe` — passed. This uses synthetic Telegram input, a disposable PostgreSQL database, the real conversation dispatcher/office-selection handler, an injected crash after Case commit and before inbox acknowledgement, then replay through a fresh worker after in-process state is cleared. It verifies one Case, one lifecycle event, safe restart guidance, and eventual encrypted-inbox payload cleanup.
- `tests/test_postgres_privilege_hardening.py::test_pairing_privilege_migration_revokes_structural_grants` — passed. It seeds excess privileges in a test database, applies `db/migrations/20261026130000_revoke_excess_external_identity_pairing_privileges.sql` twice, and verifies `TRUNCATE`, `REFERENCES`, and `TRIGGER` are removed from `PUBLIC`, `anon`, `authenticated`, and `service_role`.
- The focused test job, branch-budget gate, API runtime smoke, WebApp runtime smoke, PostgreSQL RLS/identity/inbox/continuity, backup/restore and restart-durability gates also passed in this CI run.

### Supabase/read-only findings that remain release gates

- The new pairing privilege migration is **not applied to production**. A read-only query still observed `TRUNCATE`, `REFERENCES`, and `TRIGGER` privileges on `public.external_identity_pairings` for `anon`, `authenticated`, and `service_role`. Apply only through the reviewed migration/promotion process, then re-query the live catalog to establish the resulting state.
- RLS is disabled on the inspected project's `civic_cases`, `civic_case_events`, `civic_case_consents`, `civic_case_submissions`, `external_identity_links`, `external_identity_pairings`, `telegram_update_inbox`, `janavani_delegation_grants`, and `janavani_service_identity_policies`. Previous grants review did not establish anonymous direct DML on these tables, so this observation is a hardening gate, not proof of an anonymous data-exfiltration path. Do not enable RLS without testing the intended dedicated runtime-role model and both positive/negative owner-isolation cases.
- The inspected Supabase project reports `public.offices` has zero rows and `to_regclass('public.civic_authorities')` is null. The source has a canonical `PostgresAuthorityRepository` for `civic_authorities`, while the existing public `offices` table is a different schema. Confirm which DSN is actually used by the production runtime before planning a migration or importing data. Do not invent or auto-seed authority records; import only source-backed records and mark verification status explicitly.
- The candidate now removes constructor-time `_initialize()` from `PostgresAuthorityRepository`. `db/migrations/20261026140000_create_civic_authorities.sql` owns the `public.civic_authorities` table/index, and `tests/test_postgres_authority_repository.py` verifies construction does not open the database or run DDL and that the migration is idempotent. Both tests passed in CI. The inspected live Supabase project still has no `public.civic_authorities` table; the migration has not been applied there, and source-backed records still need to be reconciled/imported through the approved process.
- Railway's production `janavani-telegram-webhook` service still runs the previously verified commit `649d3f36e61ab0db7b9b368737c7ca1d8aa39694` from `chore/ecosystem-shared-capability-infrastructure`. The latest candidate commits and privilege migration have **not** been deployed to that service. The last `/liveness` result is process liveness only; deployed citizen-action acceptance remains outstanding.

### Branch/PR gate

The product repository still has nine physical branch refs. PR #204 remains draft and unmergeable. PR #225 requires the repository secret `JANAVANI_BRANCH_RETIRE_TOKEN` to be configured manually before the guarded archive-first retirement flow can finish; do not paste the token into a PR, source file, or chat. Do not call the physical branch count eight until a fresh GitHub branch query confirms it.

### Decision

Keep the release status **BLOCKED** until:
1. The guarded retirement process archives and deletes only the approved retirement-only ref and the repository confirms exactly eight physical refs.
2. The new SQL privilege migration is promoted under a reviewed migration procedure and live grants are verified.
3. The canonical authority provider/schema/data source is reconciled, and verified authority records are imported from primary sources.
4. The deployed-acceptance sequence above is performed against the intended running Web/API and Telegram webhook commit, including actual webhook registration, pairing, cross-surface ownership isolation, retry/dead-letter, restart recovery, and restored-backup verification.

CI success demonstrates code/test evidence only; it is not production promotion or end-to-end deployed acceptance.
