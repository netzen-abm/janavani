from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)

from core.config import Config

from tools.search_directory import search_office
from tools.rate_office import save_rating
from tools.generate_pdf import generate_complaint_pdf
from legal_brain import get_legal_advice


# --------------------------------------------------
# /start
# --------------------------------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    message = """
🇮🇳 Welcome to Janavani

Citizen Governance Platform

Available Commands

/start
/search
/rate
/complaint

Examples

/search ration Kochi

/rate 3 1 Aadhar failed

/complaint 3 Aadhar failed
"""

    await update.message.reply_text(message)


# --------------------------------------------------
# /search
# --------------------------------------------------
async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if len(context.args) < 2:

        await update.message.reply_text(
            "Usage:\n/search ration Kochi"
        )

        return

    department = context.args[0]
    location = " ".join(context.args[1:])

    result = search_office(
        department,
        location
    )

    await update.message.reply_text(result)


# --------------------------------------------------
# /rate
# --------------------------------------------------
async def rate(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if len(context.args) < 3:

        await update.message.reply_text(
            "Usage:\n/rate 3 1 Aadhar failed"
        )

        return

    office_id = context.args[0]
    rating = int(context.args[1])
    issue = " ".join(context.args[2:])

    result = save_rating(
        office_id,
        rating,
        issue
    )

    await update.message.reply_text(result)


# --------------------------------------------------
# /complaint
# --------------------------------------------------
async def complaint(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if len(context.args) < 2:

        await update.message.reply_text(
            "Usage:\n/complaint 3 Aadhar failed"
        )

        return

    office_id = context.args[0]
    issue = " ".join(context.args[1:])

    pdf = generate_complaint_pdf(
        "Citizen",
        "Kochi, Kerala",
        office_id,
        issue
    )

    await update.message.reply_text(
        f"{pdf}\n\nComplaint generated successfully."
    )


# --------------------------------------------------
# MAIN
# --------------------------------------------------
def main():

    if not Config.TELEGRAM_BOT_TOKEN:
        raise Exception("TELEGRAM_BOT_TOKEN not configured")

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

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("search", search))
    application.add_handler(CommandHandler("rate", rate))
    application.add_handler(CommandHandler("complaint", complaint))

    print("✅ Bot Started Successfully")
    print("=" * 60)

    application.run_polling(
        drop_pending_updates=True
    )


if __name__ == "__main__":
    main()
