# Telegram webhook deployment (free-tier smoke test)

Janavani uses a dedicated FastAPI webhook service for Telegram updates. The Web/API service remains independent. Do not run the polling worker and webhook for the same bot token simultaneously: Telegram supports one configured webhook, and polling conflicts with webhook delivery.

## Configure the Render free web service

1. Deploy the `janavani-telegram-webhook` service from `render.yaml`.
2. In the service dashboard, set `TELEGRAM_BOT_TOKEN` to the bot token from BotFather.
3. Set `TELEGRAM_WEBHOOK_SECRET` to a random 32+ character string containing only letters, digits, underscores or hyphens. Do not commit it.
4. Copy the actual public HTTPS service URL from Render and set `TELEGRAM_WEBHOOK_URL` to `https://<actual-service-host>/telegram/webhook`.
5. Redeploy/restart the service after setting secrets. Check `/liveness` returns HTTP 200 and inspect logs for startup/configuration errors.
6. Open https://t.me/JanaVaniBot and send `/start`, then `/help` and `/privacy`.

The service is deliberately configured with `JANAVANI_RUNTIME_MODE=test` and transient content for smoke testing. Do not submit real citizen data. Test mode is not production persistence: in-memory Case metadata and transient content can be lost on restart or free-tier sleep. The current bot command workflows may create local test state, but this is not a verified durable citizen service.

## Webhook behavior and security

- Telegram sends HTTPS POST requests to `/telegram/webhook`.
- The endpoint checks `X-Telegram-Bot-Api-Secret-Token` using constant-time comparison.
- Valid updates are queued to the existing python-telegram-bot application; existing command handlers remain the business adapter.
- The application calls `setWebhook` at startup and does not use long polling.
- `drop_pending_updates=false` preserves queued updates through service restarts where Telegram retains them.
- A free Render web service may spin down. Telegram may retry a webhook request after timeout/error; monitor webhook delivery and duplicate-update handling. Do not assume every update is processed exactly once.
- Do not expose the bot token or webhook secret in logs, URLs, client-side code or screenshots.

## Production gate

Do not change `JANAVANI_RUNTIME_MODE` to production until the PostgreSQL, identity assertion, artifact repository and object-storage settings required by `src/config/runtime.py` are configured and verified. The Case-content privacy policy must remain explicit; this webhook configuration does not authorize durable storage of citizen narratives.
