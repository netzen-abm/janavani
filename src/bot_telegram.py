from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
)

from core.config import Config

from conversation.handler import (
    start,
    search,
    rate,
    complaint,
    handle_message,

)

from conversation.router import route

def main():

    if not Config.TELEGRAM_BOT_TOKEN:
        raise Exception(
            "TELEGRAM_BOT_TOKEN not configured"
        )

    print("=" * 60)
    print("🇮🇳 JANAVANI TELEGRAM BOT")
    print("=" * 60)
    print("Starting Bot...")
    print("=" * 60)

    application = (
        Application
        .builder()
        .token(Config.TELEGRAM_BOT_TOKEN)
        .build()
    )

    # ------------------------
    # Commands
    # ------------------------

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

    # ------------------------
    # Conversation
    # ------------------------

    application.add_handler(
        MessageHandler(
    filters.TEXT & ~filters.COMMAND,
    route

        )
    )

    print("✅ Bot Started Successfully")
    print("=" * 60)

    application.run_polling(
        drop_pending_updates=True
    )


if __name__ == "__main__":
    main()
