import os
from flask import Flask
from dotenv import load_dotenv
from supabase import create_client

# Load .env locally (Render ignores if not present)
load_dotenv()

app = Flask(__name__)

# Read Supabase credentials
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")   # <-- FIXED

# Create client only if credentials exist
supabase = None

if SUPABASE_URL and SUPABASE_KEY:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


@app.route("/")
def home():
    return """
    <h1>🇮🇳 Janavani</h1>
    <h2>Citizen Governance Platform</h2>

    <p>✅ Server Running</p>

    <ul>
        <li><a href="/health">Health Check</a></li>
        <li><a href="/supabase">Supabase Test</a></li>
    </ul>
    """


@app.route("/health")
def health():
    return {
        "status": "healthy",
        "service": "Janavani"
    }


@app.route("/supabase")
def test_supabase():

    if supabase is None:
        return {
            "status": "error",
            "message": "Supabase credentials not found."
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


if __name__ == "__main__":

    port = int(os.environ.get("PORT", 10000))

    app.run(
        host="0.0.0.0",
        port=port
    )
