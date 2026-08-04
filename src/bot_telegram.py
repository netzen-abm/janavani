from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
)

from core.config import Config

# ----------------------------
# Commands
# ----------------------------

from commands.start import start
from commands.search import search
from commands.rate import rate

# from commands.complaint import complaint

# ----------------------------
# Conversation Router
# ----------------------------

from conversation.router import route


# ==========================================================
# MAIN
# ==========================================================

def main():

    # ----------------------------
    # Validate Configuration
    # ----------------------------

    if not Config.TELEGRAM_BOT_TOKEN:

        raise Exception(
            "TELEGRAM_BOT_TOKEN is not configured."
        )

    print("=" * 60)
    print("🇮🇳 JANAVANI TELEGRAM BOT")
    print("=" * 60)
    print("Starting Bot...")
    print("=" * 60)

    # ----------------------------
    # Telegram Application
    # ----------------------------

    application = (
        Application
        .builder()
        .token(Config.TELEGRAM_BOT_TOKEN)
        .build()
    )

    # ----------------------------
    # Slash Commands
    # ----------------------------

    application.add_handler(
        CommandHandler("start", start)
    )

    application.add_handler(
        CommandHandler("search", search)
    )

    application.add_handler(
        CommandHandler("rate", rate)
    )

    application.add_handler(
        CommandHandler("complaint", complaint)
    )

    # ----------------------------
    # Normal Conversation
    # ----------------------------

    application.add_handler(

        MessageHandler(

            filters.TEXT & ~filters.COMMAND,

            route

        )

    )

    print("✅ Bot Started Successfully")
    print("=" * 60)

    # ----------------------------
    # Run Bot
    # ----------------------------

    application.run_polling(

        drop_pending_updates=True

    )


# ==========================================================
# ENTRY POINT
# ==========================================================

if __name__ == "__main__":

    main()
