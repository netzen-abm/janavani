import os

from flask import Flask
from dotenv import load_dotenv
from supabase import create_client

# ==========================================
# Load Environment Variables
# ==========================================

load_dotenv()

app = Flask(__name__)

# ==========================================
# Supabase Configuration
# ==========================================

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")

supabase = None

if SUPABASE_URL and SUPABASE_KEY:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ==========================================
# Home
# ==========================================

@app.route("/")
def home():

    return """
    <html>

    <head>
        <title>Janavani</title>
    </head>

    <body>

        <h1>🇮🇳 Janavani</h1>

        <h2>Citizen Governance Platform</h2>

        <hr>

        <p>✅ Web Server Running</p>

        <ul>
            <li><a href="/health">Health Check</a></li>
            <li><a href="/supabase">Supabase Test</a></li>
        </ul>

    </body>

    </html>
    """

# ==========================================
# Health Check
# ==========================================

@app.route("/health")
def health():

    return {
        "status": "healthy",
        "service": "Janavani Web",
        "database": "connected" if supabase else "not configured"
    }

# ==========================================
# Supabase Test
# ==========================================

@app.route("/supabase")
def supabase_test():

    if supabase is None:

        return {
            "status": "error",
            "message": "Supabase environment variables not configured."
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
            "rows": response.data
        }

    except Exception as e:

        return {
            "status": "failed",
            "error": str(e)
        }, 500

# ==========================================
# Main
# ==========================================

if __name__ == "__main__":

    print("=" * 50)
    print("Starting Janavani Web Server...")
    print("=" * 50)

    port = int(os.environ.get("PORT", 10000))

    app.run(
        host="0.0.0.0",
        port=port
    )
