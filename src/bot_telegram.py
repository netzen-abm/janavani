"""Janavani Telegram webhook runtime.

This adapter is deployed independently from the WebApp. Do not use polling:
the platform receives Telegram updates through the configured HTTPS webhook.
"""
import os

from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    MessageHandler,
    filters,
)

from core.config import Config
from commands.check import check
from commands.start import start
from commands.search import search
from commands.rate import rate
from commands.complaint import complaint
from conversation.router import route
from conversation.steps.format import handle_format


def build_application() -> Application:
    """Build the Telegram application and register existing handlers."""
    if not Config.TELEGRAM_BOT_TOKEN:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is not configured.")

    application = Application.builder().token(Config.TELEGRAM_BOT_TOKEN).build()
    application.add_handler(CallbackQueryHandler(handle_format))
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("search", search))
    application.add_handler(CommandHandler("rate", rate))
    application.add_handler(CommandHandler("complaint", complaint))
    application.add_handler(CommandHandler("check", check))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, route))
    return application


def main() -> None:
    """Run the bot using Telegram's HTTPS webhook delivery."""
    webhook_secret = os.getenv("TELEGRAM_WEBHOOK_SECRET", "")
    if not webhook_secret:
        raise RuntimeError("TELEGRAM_WEBHOOK_SECRET must be configured for webhook mode.")

    port = int(os.getenv("PORT", "10000"))
    webhook_url = os.getenv("TELEGRAM_WEBHOOK_URL", "").rstrip("/")
    if not webhook_url:
        external_url = os.getenv("RENDER_EXTERNAL_URL", "").rstrip("/")
        if not external_url:
            raise RuntimeError(
                "Set TELEGRAM_WEBHOOK_URL or deploy on a platform exposing RENDER_EXTERNAL_URL."
            )
        webhook_url = f"{external_url}/telegram/webhook"

    print("Starting Janavani Telegram bot in webhook mode.")
    application = build_application()
    application.run_webhook(
        listen="0.0.0.0",
        port=port,
        url_path="telegram/webhook",
        webhook_url=webhook_url,
        secret_token=webhook_secret,
        drop_pending_updates=False,
    )


if __name__ == "__main__":
    main()
