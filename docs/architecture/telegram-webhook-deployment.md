# Janavani Telegram Webhook — Production Deployment Runbook

**Status:** Release-blocked until hosting secrets and end-to-end checks are complete  
**Reviewed:** 26 October 2026

This runbook describes the canonical Python webhook runtime. The existing Bun Function is a legacy fallback and uses process-local duplicate suppression; it must not be presented as the durable Case-tracking product or independently compete to register Telegram's webhook.

## Runtime topology

```text
Telegram Bot API
  │ HTTPS POST + secret-token header
  ▼
Railway public URL /telegram/webhook
  │ validate secret + bound body + parse update
  ▼
PostgreSQL inbox
  │ encrypt payload with Fernet before commit
  ▼
Inbox worker
  │ invoke the canonical Telegram Application / shared capability graph
  ▼
Citizen-owned draft or explicitly authorized tracked Case
```

Anonymous drafting is the first journey. It must not create an account or Case, persist the user's narrative as a Case, or claim the complaint/RTI was submitted. The `/account` command is a separate opt-in for persistent tracking. Cross-device continuity needs shared PostgreSQL identity links and explicit account pairing.

## Configure the canonical Railway Python service

1. Open the `telegram-bot` service in the Janavani Railway project and confirm its source is `netzen-abm/janavani`. Use the release commit from the reviewed pull request; do not deploy an unreviewed branch directly to production.
2. Set the start command to run the FastAPI webhook, not polling:

   ```sh
   sh -c 'cd /workspace && export PYTHONPATH=/workspace && exec uvicorn src.web.telegram_webhook_app:app --host 0.0.0.0 --port ${PORT:-8080}'
   ```

3. Configure the variables below in Railway's server-side Variables panel. Never paste real secrets into GitHub, source files, build arguments, screenshots, public issues, or client code.

| Variable | Required value / rule |
|---|---|
| `JANAVANI_RUNTIME_MODE` | `production` |
| `TELEGRAM_BOT_TOKEN` | Token from BotFather; keep server-side |
| `TELEGRAM_WEBHOOK_URL` | Exact public HTTPS URL ending in `/telegram/webhook` for the canonical Python webhook |
| `TELEGRAM_WEBHOOK_SECRET` | Random 32–256 character URL-safe value; must match Telegram's secret-token header |
| `JANAVANI_TELEGRAM_INBOX_DSN` | PostgreSQL connection URI using a dedicated least-privilege role allowed to access the encrypted Telegram inbox |
| `JANAVANI_TELEGRAM_INBOX_ENCRYPTION_KEYS` | One or more comma-separated valid Fernet keys; first key encrypts new payloads, later keys permit rotation/decryption |
| `JANAVANI_CASE_REPOSITORY_PROVIDER` | `postgres` |
| `JANAVANI_ARTIFACT_REPOSITORY_PROVIDER` | `postgres` |
| `JANAVANI_EVIDENCE_REPOSITORY_PROVIDER` | `postgres` |
| `JANAVANI_AUTHORITY_REPOSITORY_PROVIDER` | `postgres` |
| `JANAVANI_CONSENT_REPOSITORY_PROVIDER` | `postgres` |
| `JANAVANI_SUBMISSION_REPOSITORY_PROVIDER` | `postgres` |
| `JANAVANI_EXTERNAL_IDENTITY_LINKS_REPOSITORY_PROVIDER` | `postgres` |
| `JANAVANI_POSTGRES_DSN` | Canonical PostgreSQL DSN for the shared Case and consent repositories |
| `JANAVANI_IDENTITY_LINKS_DSN` | Dedicated least-privilege PostgreSQL DSN for external identity mappings and pairing |
| `JANAVANI_DOCUMENT_REVIEW_REPOSITORY_PROVIDER` | `transient` |
| `JANAVANI_ARTIFACT_BLOB_PROVIDER` | `s3` |
| `JANAVANI_ARTIFACT_S3_BUCKET` | Provisioned bucket used by the canonical document-artifact repository |
| `JANAVANI_IDENTITY_ASSERTION_SECRET` | At least 32 characters; required for authenticated internal trust |
| `JANAVANI_IDENTITY_ASSERTION_ISSUER` | `janavani-identity` or the configured trusted issuer |
| `JANAVANI_IDENTITY_ASSERTION_AUDIENCE` | `janavani-api` or the configured audience |

The artifact repository also needs its server-side S3 endpoint/credential configuration if the selected provider requires it. Use the existing approved provider setup; do not switch persisted production domains to memory just to make startup pass. Follow the applicable least-privilege table grants and RLS policy rather than using an administrative database credential for every component.

For local development, generate a Fernet key using a trusted local Python installation with `from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())`. Store it directly in the hosting secret manager; never commit the generated value. For rotation, put the new key first and retain previous valid keys for decryption until old encrypted payloads and required retention windows have expired.

## Webhook lifecycle

- The canonical Python process validates configuration and the encryption key ring before registering the webhook.
- PostgreSQL inbox DDL must already be applied. Confirm `telegram_update_inbox` and its encrypted-payload fields are present.
- Updates are accepted only after a successful encrypted durable write. Database errors return a retryable response; do not acknowledge an update that is not durably stored.
- Inbox retention and retries are bounded. Verify dead-letter behavior, expiry enforcement, worker restart recovery, idempotency and key rotation before production traffic.
- Do not run polling and webhook consumption simultaneously for the same bot token.
- Do not let the legacy Bun Function register or redirect `setWebhook` while the canonical Python service owns registration.

## Account choices and trust boundary

- Telegram bot users are identified only by a verified Telegram update. A user-typed Telegram ID is not proof of ownership.
- `/account` is explicit opt-in, private-chat only, and requires the configured PostgreSQL identity repository.
- Web sign-in uses the configured OIDC provider only after its issuer, redirect URI, client credentials, state, nonce, PKCE, issuer/audience/signature and session settings are validated.
- Web and bot identities remain separate until the user confirms an explicit cross-surface pairing flow.
- Email OTP, SMS/mobile OTP, and generated key-pair sign-in are not available until their verification, throttling, recovery, revocation, and security tests pass.
- A public key may identify a credential; a private key must never be uploaded or logged. Prefer a reviewed WebAuthn/passkey flow or local cryptographic operations with explicit backup/recovery behavior.
- Authentication does not grant administrator rights, authorize delivery, or imply consent to submit a document.

## Release checklist

- [ ] The feature PR is reviewed and required GitHub checks pass on its exact head SHA.
- [ ] A fresh deployment uses the reviewed commit and the canonical webhook start command.
- [ ] All required variables exist in the correct Railway environment; none are logged or included in the image.
- [ ] The public domain routes to the service's actual listening port, with TLS active.
- [ ] Telegram `getWebhookInfo` reports the canonical URL, expected allowed updates, and no persistent delivery errors.
- [ ] Valid secret accepts an update; missing/wrong secret is rejected.
- [ ] Oversized/malformed payloads are rejected.
- [ ] Test messages are encrypted in PostgreSQL before HTTP acknowledgement; plaintext payloads do not appear in rows/logs.
- [ ] Worker restart, duplicate delivery, retries, expiry, key rotation and database failure have been exercised.
- [ ] Anonymous draft flow works without OIDC or account identity.
- [ ] `/account` fails closed without shared identity storage and succeeds only with a verified private Telegram update.
- [ ] Cross-surface pairing proves both sessions and requires explicit confirmation.
- [ ] A harmless staging complaint/RTI is reviewed and downloaded; no authority submission occurs without its explicit authorized workflow.
- [ ] Public WebApp preview and live end-to-end Telegram tests pass before product readiness is claimed.

## Observed blockers on 26 October 2026

- The existing canonical Python Railway bot deployment is `CRASHED` and has no configured service variables in the inspected Railway environment.
- The separate Bun webhook Function is `SLEEPING` and is explicitly marked legacy fallback. Its current variables do not include `JANAVANI_TELEGRAM_INBOX_DSN` or `JANAVANI_TELEGRAM_INBOX_ENCRYPTION_KEYS`.
- The active Supabase project contains the canonical inbox and identity migrations, but the connected tools do not provide the database password/connection URI. Do not invent a DSN; configure a dedicated connection URI securely through the database owner/secret manager.
- The WebApp preview create request returned HTTP 402 due to Vercel's free-tier deployment quota exhaustion window.
- The repository had nine physical branches at the last inventory. The governed transition to eight branches requires PR #213's independent approval and the real GitHub main ruleset to be corrected; do not delete branches outside that controlled archive-before-delete process.

**Do not mark the public Telegram product or WebApp as deployed until the release checklist passes against the live services.**
