import subprocess
import os

from flask import Flask

from core.config import Config
from database.supabase import supabase

app = Flask(__name__)


# ---------------------------------------------------
# Home
# ---------------------------------------------------
@app.route("/")
def home():
    return """
    <h1>🇮🇳 Janavani</h1>
    <h2>Citizen Governance Platform</h2>

    <p>✅ Flask Running</p>

    <ul>
        <li><a href="/health">Health Check</a></li>
        <li><a href="/supabase">Supabase Test</a></li>
    </ul>
    """


# ---------------------------------------------------
# Health
# ---------------------------------------------------
@app.route("/health")
def health():

    return {
        "status": "healthy",
        "database": "connected" if supabase else "not configured"
    }


# ---------------------------------------------------
# Supabase Test
# ---------------------------------------------------
@app.route("/supabase")
def supabase_test():

    if supabase is None:

        return {
            "status": "error",
            "message": "Supabase is not configured."
        }, 500

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
            "count": len(response.data),
            "rows": response.data
        }

    except Exception as e:

        return {
            "status": "failed",
            "error": str(e)
        }, 500


# ---------------------------------------------------
# Main (legacy developer-mode guarded)
# ---------------------------------------------------
if __name__ == "__main__":

    print("=" * 50)
    print("Starting Janavani Web Server")
    print("=" * 50)

    # Developer-controlled behavior: only start the Telegram bot as a subprocess
    # when the environment variable START_TELEGRAM_FOR_LOCAL is set to a truthy value.
    start_telegram = os.getenv("START_TELEGRAM_FOR_LOCAL", "false").lower() in ("1", "true", "yes")

    if start_telegram:
        print("WARNING: Starting Telegram bot as a child process. This is intended for local development only.")
        try:
            bot_process = subprocess.Popen(
                ["python3", "-u", "src/bot_telegram.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
            )

            print(f"Telegram Bot PID: {bot_process.pid}")
            print("Telegram Bot Started (dev mode)")

        except Exception as exc:
            print("Failed to start Telegram bot as subprocess:", exc)
            bot_process = None

    else:
        print("Starting Web server in independent runtime mode. Telegram bot will NOT be started as a subprocess.")
        bot_process = None

    try:
        app.run(
            host="0.0.0.0",
            port=Config.PORT,
            debug=False
        )
    finally:
        # Attempt graceful shutdown of dev-mode bot if we started it
        try:
            if bot_process:
                bot_process.terminate()
                bot_process.wait(timeout=5)
        except Exception:
            pass
