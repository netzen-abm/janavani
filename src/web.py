import os
import threading

from flask import Flask
from dotenv import load_dotenv
from supabase import create_client

# ----------------------------
# Load Environment Variables
# ----------------------------
load_dotenv()

app = Flask(__name__)

# ----------------------------
# Supabase
# ----------------------------
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")

supabase = None

if SUPABASE_URL and SUPABASE_KEY:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ----------------------------
# Telegram Bot
# ----------------------------
def start_telegram_bot():
    from src.bot_telegram import main
    main()

# ----------------------------
# Routes
# ----------------------------
@app.route("/")
def home():
    return """
    <h1>🇮🇳 Janavani</h1>
    <h2>Citizen Governance Platform</h2>

    <p>✅ Flask Running</p>

    <ul>
        <li><a href="/health">Health</a></li>
        <li><a href="/supabase">Supabase Test</a></li>
    </ul>
    """

@app.route("/health")
def health():
    return {
        "status": "healthy",
        "telegram": "running",
        "database": "connected" if supabase else "not connected"
    }

@app.route("/supabase")
def supabase_test():

    if supabase is None:
        return {
            "status": "error",
            "message": "Supabase not configured"
        }

    try:

        response = (
            supabase
            .table("offices")
            .select("*")
            .limit(5)
            .execute()
        )

        return {
            "status": "connected",
            "rows": response.data
        }

    except Exception as e:

        return {
            "status": "failed",
            "error": str(e)
        }, 500

# ----------------------------
# Main
# ----------------------------
if __name__ == "__main__":

    print("===================================")
    print("Starting Janavani Platform...")
    print("===================================")

    # Start Telegram Bot
    threading.Thread(
        target=start_telegram_bot,
        daemon=True
    ).start()

    print("✅ Telegram Bot Started")

    port = int(os.environ.get("PORT", 10000))

    app.run(
        host="0.0.0.0",
        port=port
    )
