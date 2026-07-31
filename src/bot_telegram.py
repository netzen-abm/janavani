# src/bot_telegram.py
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

from src.tools.search_directory import search_office
from src.tools.rate_office import save_rating
from src.tools.generate_pdf import generate_complaint_pdf
from src.legal_brain import get_legal_advice

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = "Namaste! I am Janavani Bot 🇮🇳\n\nCommands:\n/search ration Kochi\n/rate 3 1 Aadhar failed\n/complaint 3 Aadhar failed"
    await update.message.reply_text(msg)

async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        await update.message.reply_text("Use: /search ration Kochi")
        return
    result = search_office(context.args[0], context.args[1])
    await update.message.reply_text(result)

async def rate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 3:
        await update.message.reply_text("Use: /rate 3 1 Aadhar failed")
        return
    office_id, rating = context.args[0], int(context.args[1])
    issue = " ".join(context.args[2:])
    result = save_rating(office_id, rating, issue)
    await update.message.reply_text(result)

async def complaint(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        await update.message.reply_text("Use: /complaint 3 Aadhar failed")
        return
    office_id = context.args[0]
    issue = " ".join(context.args[1:])
    pdf = generate_complaint_pdf("Citizen", "Kochi, Kerala", office_id, issue)
    await update.message.reply_text(f"{pdf}\n\nSend this PDF to the office.")

def main():
    app = Application.builder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("search", search))
    app.add_handler(CommandHandler("rate", rate))
    app.add_handler(CommandHandler("complaint", complaint))
    app.run_polling()

if __name__ == "__main__":
    main()
