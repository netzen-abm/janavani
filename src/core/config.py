import os

from dotenv import load_dotenv

load_dotenv()


class Config:

    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")

    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

    PORT = int(os.getenv("PORT", 10000))
