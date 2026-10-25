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
- [ ] Production provider configuration passes `validate_runtime_configuration()`; no process-local fallback is used for durable Case, artifact, evidence, consent, submission, authority-directory or identity-link state.
- [ ] `JANAVANI_AUTHORITY_REPOSITORY_PROVIDER=postgres` is configured in production. The shared directory is seeded with source-backed records, and only records explicitly marked verified with a usable destination are offered to citizens.
- [ ] Artifact storage, citizen-content retention/deletion policy, migration state, backup/restore and operational alerting are approved.
- [ ] The trusted identity gateway is the only issuer of short-lived signed identity assertions; issuer/audience/signature/expiry are validated server-side. Browser-provided principal IDs are never trusted.
- [ ] Telegram webhook secret is configured in the provider and service; webhook URL is HTTPS and points to the actual deployed Telegram service.

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
- [ ] Submit the same synthetic Telegram `update_id` twice; duplicate delivery is acknowledged without duplicate inbox work or duplicate business effects.
- [ ] Simulate a transient database outage in staging; webhook acceptance fails retryably (HTTP 503) rather than acknowledging an unpersisted update.
- [ ] Stop a worker while a synthetic update is pending, restart it, and verify the update is processed or reaches the documented retry/dead-letter terminal state.
- [ ] Run concurrent workers and verify stale lease holders cannot commit after their claim has been fenced.
- [ ] Replay an update that would trigger a consequential action; prove the domain operation has its own idempotency guard. Inbox deduplication alone is not enough.
- [ ] Verify retry limits, dead-letter visibility, payload cleanup/retention and alerting.

**Pass:** No acknowledged update is silently lost, stale workers cannot commit, and replay cannot duplicate consequential business effects.

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
