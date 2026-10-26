# Janavani Telegram webhook — Railway Function

This directory records the source snapshot for the minimal Bun-based Railway Function deployed as service `janavani-telegram-webhook` in project `janavani-telegram-bot`.

## Runtime configuration

Set these variables in the Railway service's encrypted Variables interface:

- `TELEGRAM_BOT_TOKEN`: bot token from Telegram BotFather. Keep it out of GitHub and chat.
- `TELEGRAM_WEBHOOK_URL`: `https://janavani-telegram-webhook-production.up.railway.app/telegram/webhook`
- `TELEGRAM_WEBHOOK_SECRET`: a secret token of 1–256 characters using only Telegram's supported letters, digits, underscore, and hyphen. The deployed service currently has a generated 64-character value; don't paste it into GitHub.

After `TELEGRAM_BOT_TOKEN` is configured, request `/health` once. The handler calls Telegram's `setWebhook` API and reports readiness only if registration succeeds. `/livez` is a process-liveness endpoint; `/health` and `/readyz` are readiness endpoints. The webhook path is `/telegram/webhook`.

## Supported demo behavior

- `/start`, `/help`, `/complaint`, and `/rti`
- Generic response for plain-text messages
- Timing-safe webhook-secret comparison
- Bounded request body and JSON validation
- Sanitized logs that do not include message contents or credentials

## Explicit limitations

This is a public demonstration adapter, **not** a production civic-case intake service. It does not persist Cases or citizen conversation state. Duplicate-update memory is process-local and is lost on restart. A successful deployment is not proof that the bot is activated; verify the Railway readiness endpoint and then test a real Telegram conversation.

The intended durable path already in the repository is `src/web/telegram_webhook_app.py` with `src/web/telegram_inbox_worker.py` and the encrypted PostgreSQL inbox. Migrate this temporary function only after its database, encryption-key, replay, and post-commit failure acceptance tests pass.

## Change-control note

Railway Function source is currently deployed directly through Railway and is **not automatically redeployed by a Git push**. Keep this file synchronized with the running function. Before changing the function, review the entire source, deploy it, inspect the exact deployment state, and exercise the health and webhook rejection paths.
