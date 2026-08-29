# ============================================
# JANAVANI — PRODUCTION ENTRY POINT
# ============================================

from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)

from core.config import Config

# Commands
from commands.start import start
from commands.search import search
from commands.rate import rate
from commands.complaint import complaint
from commands.check import check

# Conversation Router
from conversation.router import route

# Format Button Handler
from conversation.steps.format import handle_format


def main():
    # --------------------------------------
    # 🔐 CONFIG VALIDATION
    # --------------------------------------
    if not Config.TELEGRAM_BOT_TOKEN:
        raise Exception("❌ TELEGRAM_BOT_TOKEN is not configured.")

    print("=" * 60)
    print("🇮🇳 JANAVANI TELEGRAM BOT")
    print("=" * 60)
    print("Starting Bot...")
    print("=" * 60)

    # --------------------------------------
    # 🚀 BUILD APPLICATION
    # --------------------------------------
    application = (
        Application.builder()
        .token(Config.TELEGRAM_BOT_TOKEN)
        .build()
    )

    # --------------------------------------
    # 🔘 CALLBACK HANDLERS (BUTTONS)
    # --------------------------------------
    application.add_handler(CallbackQueryHandler(handle_format))

    # --------------------------------------
    # 🧭 COMMAND HANDLERS
    # --------------------------------------
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("search", search))
    application.add_handler(CommandHandler("rate", rate))
    application.add_handler(CommandHandler("complaint", complaint))
    application.add_handler(CommandHandler("check", check))

    # --------------------------------------
    # 💬 MESSAGE ROUTER (CORE ENGINE)
    # --------------------------------------
    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            route
        )
    )

    # --------------------------------------
    # ✅ START BOT
    # --------------------------------------
    print("✅ Bot Started Successfully")
    print("=" * 60)

    application.run_polling(drop_pending_updates=True)


# --------------------------------------
# 🏁 ENTRY POINT (FIXED)
# --------------------------------------
if __name__ == "__main__":
    main()