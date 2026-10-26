# Telegram webhook deployment and reliability contract

Janavani's Telegram webhook is an independent access-surface runtime. It must use shared capability implementations and must not become a second Case/business-logic implementation.

## Before deployment

1. Apply `db/migrations/20261012120000_telegram_update_inbox.sql` and `db/migrations/20261025120000_telegram_inbox_encrypted_payloads.sql` to the Telegram inbox database.
2. Configure `TELEGRAM_BOT_TOKEN` from BotFather.
3. Configure `TELEGRAM_WEBHOOK_SECRET` with a random 32–256 character URL-safe value. Never commit it.
4. Configure `TELEGRAM_WEBHOOK_URL` to the public HTTPS endpoint ending in `/telegram/webhook`.
5. Configure `JANAVANI_TELEGRAM_INBOX_DSN` with a PostgreSQL DSN held in the deployment secret manager. Grant the runtime role `USAGE` on schema `public` and `SELECT, INSERT, UPDATE` on `public.telegram_update_inbox`; do not grant table ownership or `DELETE` unless a separately reviewed operation requires it.
6. Ensure no polling process uses the same bot token. Webhook and polling must not run concurrently for one bot.
7. Deploy/restart and verify health, webhook registration, inbox insertion, processing, retry, and restart recovery.

Production startup fails closed if the inbox DSN is missing. Do not use production citizen data until inbox and Case/evidence/document persistence are independently verified.

## Acceptance and processing

- The endpoint validates Telegram's secret header in constant time and limits request bodies to 1 MiB.
- Each update is stored in `public.telegram_update_inbox` using Telegram's `update_id` as an idempotency key.
- HTTP 202 is returned only after the database insert/duplicate check completes. Duplicate update IDs do not create duplicate inbox rows. Database errors return HTTP 503 for retry.
- A worker claims rows using `FOR UPDATE SKIP LOCKED`, renews processing leases, retries failures with bounded backoff, and dead-letters after the configured attempt limit.
- Terminal rows retain the update ID and status but clear the payload to reduce message-content retention.
- The guarantee is **at-least-once delivery to handler dispatch**, not exactly-once business execution. A crash after a handler performs an effect but before the inbox row is marked processed can cause a retry. Consequential capabilities need their own idempotency and transaction guarantees.
- Polling now uses `drop_pending_updates=False`, avoiding intentional deletion of Telegram pending updates. This is not a replacement for the durable webhook inbox.

## Privacy and release gates

The inbox stores update payloads while work is pending or processing. Apply least-privilege database permissions, a retention policy, encrypted transport/storage, backups and monitoring appropriate to message sensitivity. Do not grant broad database ownership just for convenience.

The inbox alone does not make Case, evidence or document state durable. Production mode must also satisfy the provider requirements in `src/config/runtime.py`, trusted identity assertion validation, cross-user authorization, object-storage policy, and backup/restore verification. Test Web/API and Telegram independently. Do not describe a smoke-test deployment as a complete production civic service until these gates pass.


## Railway and Supabase release configuration

The canonical webhook is `src.web.telegram_webhook_app:app`. It is the only component permitted to call Telegram's `setWebhook` for this bot. Do not run `src/bot_telegram.py` polling and the webhook service concurrently with the same bot token.

### Railway service settings

- Start command: `sh -c 'exec uvicorn src.web.telegram_webhook_app:app --host 0.0.0.0 --port ${PORT:-8000}'`
- `PORT=8000` must match the Railway public domain's target port.
- Healthcheck path: `/liveness`
- Keep sleep mode enabled on a Railway Free service; request-driven wake-up is a free-tier constraint. Conversation correctness must not depend on memory surviving a sleep/restart.
- Enable IPv6 egress only if using Supabase's direct IPv6-only PostgreSQL endpoint. If using the Supabase Session Pooler, use the exact hostname and username from the Supabase Dashboard's **Connect** panel instead of guessing the pooler host.

### Runtime roles and credentials

The migrations create these deliberately restricted roles:

- `janavani_telegram_inbox_runtime` — inbox read/insert/update only.
- `janavani_civic_case_runtime` — the granted Case/consent metadata tables.
- `janavani_identity_link_runtime` — external-identity and pairing tables only.

They are created with `NOLOGIN`. Before deployment, set a separate high-entropy password for each role in the Supabase SQL Editor / secret-management workflow. Never commit passwords or post them in chat. Then add the following server-side Railway variables to the canonical Telegram service:

- `JANAVANI_TELEGRAM_INBOX_DSN` — DSN using `janavani_telegram_inbox_runtime`.
- `JANAVANI_POSTGRES_DSN` — DSN using `janavani_civic_case_runtime`.
- `JANAVANI_IDENTITY_LINKS_DSN` — DSN using `janavani_identity_link_runtime`.
- `JANAVANI_TELEGRAM_INBOX_ENCRYPTION_KEYS` — one active Fernet key (Base64 URL-safe encoding of 32 random bytes); keep old keys in the comma-separated key ring while ciphertext encrypted with those keys may still be pending.
- `TELEGRAM_BOT_TOKEN` and `TELEGRAM_WEBHOOK_SECRET` — resolve from the current secret store or set directly in Railway's encrypted Variables UI. Do not include either value in source control.
- `TELEGRAM_WEBHOOK_URL` — the canonical Railway HTTPS domain ending in `/telegram/webhook`.

For Supabase direct connections, a DSN has the form `postgresql://<runtime-role>:<password>@db.sysiblufgixbqqsdbywn.supabase.co:5432/postgres?sslmode=require&connect_timeout=8`. This form requires working IPv6 egress. Prefer the exact Session Pooler DSN from the Dashboard if direct networking is unavailable.

### Release ordering

1. Verify the runtime roles can log in and each role can perform only its required table operations.
2. Configure all required secrets and provider settings before connecting the service to the canonical webhook source.
3. Deploy with `/liveness`; verify HTTP 200, successful webhook registration, and that Telegram's configured webhook points to this canonical domain.
4. Deliver a real private-chat update. Verify durable encrypted inbox insertion, worker claim, response, terminal payload clearing, and duplicate redelivery behavior.
5. Test a restart while an update is pending and confirm it is recovered without losing workflow state.
6. Only then retire the previous receiver. Never use a healthy container or green CI as a substitute for a real Telegram end-to-end test.

### First-user product gates

A durable inbox is necessary but not sufficient for the first user release. The canonical Case metadata is separate from citizen-authored content. Current document review and Case narrative policies are intentionally transient; do not promise that complaint narratives or drafts survive restarts until an approved content-storage adapter and its retention/consent controls are implemented. The production runtime additionally requires all provider contracts, trusted identity assertions, durable artifact metadata/object storage, WebApp OIDC, owner-isolation tests, and backup/restore verification. Do not set `JANAVANI_RUNTIME_MODE=production` until every condition in `src/config/runtime.py` is met and tested.
