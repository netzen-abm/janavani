    # src/bot_telegram.py
    from telegram import Update
    from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
    from src.tools.search_directory import search_office
    from src.tools.rate_office import save_rating
    from src.tools.generate_pdf import generate_complaint_pdf
    import os

    async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("Namaste! I am Janavani. Send: /search ration Kochi")

    async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):
        args = context.args
        if len(args) < 2:
            await update.message.reply_text("Use: /search ration Kochi")
            return
        result = search_office(args[0], args[1])
        await update.message.reply_text(result)

    def main():
        app = Application.builder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("search", search))
        app.run_polling()

    if __name__ == "__main__":
        main()
