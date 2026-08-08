from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)

from core.config import Config

from commands.check import check

# Commands
from commands.start import start
from commands.search import search
from commands.rate import rate
from commands.complaint import complaint

# Conversation
from conversation.router import route

# Format buttons
from conversation.steps.format import handle_format


def main():

    # Validate config
    if not Config.TELEGRAM_BOT_TOKEN:
        raise Exception("TELEGRAM_BOT_TOKEN is not configured.")

    print("=" * 60)
    print("🇮🇳 JANAVANI TELEGRAM BOT")
    print("=" * 60)
    print("Starting Bot...")
    print("=" * 60)

    # Build app
    application = (
        Application
        .builder()
        .token(Config.TELEGRAM_BOT_TOKEN)
        .build()
    )

    # Button handler
    application.add_handler(CallbackQueryHandler(handle_format))

    # Commands
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("search", search))
    application.add_handler(CommandHandler("rate", rate))
    application.add_handler(CommandHandler("complaint", complaint))

    application.add_handler(
    CommandHandler("check", check)
)

    # Messages
    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            route
        )
    )

    print("✅ Bot Started Successfully")
    print("=" * 60)

    application.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()