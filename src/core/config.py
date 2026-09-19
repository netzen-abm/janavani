import os

from dotenv import load_dotenv

load_dotenv()


class Config:

    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

    PORT = int(os.getenv("PORT", 10000))
