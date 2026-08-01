from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import os

TOKEN = os.getenv("TELEGRAM_TOKEN") # we will set this in Render

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Welcome to Janavani Citizen Bot 🙏\n\n"
        "Voice of the People\n"
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

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("rate", rate))
    app.add_handler(CommandHandler("petition", petition))
    app.add_handler(CommandHandler("scorecard", scorecard))
    app.add_handler(CommandHandler("about", about))
    app.add_handler(CommandHandler("contact", contact))
    print("Bot is running...")
    app.run_polling()
