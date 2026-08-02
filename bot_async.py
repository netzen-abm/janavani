import os
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Load environment variables
load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN") or os.getenv("TOKEN")
if not TOKEN:
    raise SystemExit("TELEGRAM_TOKEN (or TOKEN) environment variable not set")

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# Async handlers (PTB v20+ style)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Welcome to Janavani Citizen Bot 🙏\n\n"
        "Voice of the People\n\n"
        "Use the menu below:\n"
        "/rate - Rate your government visit\n"
        "/petition - Submit a petition\n"
        "/scorecard - View scorecard\n"
        "/about - About Janavani\n"
        "/contact - Contact us"
    )

async def rate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Got it! Let's rate your govt visit. Reply with 1-5 stars")

async def petition(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Please type your petition and send it to us.")

async def scorecard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Coming soon: Your govt office scorecard")

async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Janavani: Free tool to hold govt offices accountable")

async def contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Contact us: janavani@netzen.org")


def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("rate", rate))
    app.add_handler(CommandHandler("petition", petition))
    app.add_handler(CommandHandler("scorecard", scorecard))
    app.add_handler(CommandHandler("about", about))
    app.add_handler(CommandHandler("contact", contact))

    logging.info("Bot is starting...")
    app.run_polling()


if __name__ == "__main__":
    main()
