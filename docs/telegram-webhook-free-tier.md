# Telegram webhook deployment and reliability contract

Janavani's Telegram webhook is an independent access-surface runtime. It must use shared capability implementations and must not become a second Case/business-logic implementation.

## Before deployment

1. Apply `db/migrations/20261012120000_telegram_update_inbox.sql` to the bot's PostgreSQL database.
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
