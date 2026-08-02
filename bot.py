import os
import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TOKEN")

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Welcome to Janavani Citizen Bot!\n\n"
        "I help you file civic complaints in Kerala.\n"
        "Commands:\n"
        "/rate - Rate a govt office\n"
        "/petition - File a petition\n"
        "/scorecard - View scorecard\n"
        "/about - About us\n"
        "/contact - Contact"
    )

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
