import os
from flask import Flask
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

app = Flask(__name__)

# Read Supabase credentials
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Connect to Supabase
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


@app.route("/")
def home():
    return """
    <h1>🇮🇳 Janavani</h1>
    <h3>Citizen Governance Platform</h3>
    <p>Status: Running ✅</p>
    """


@app.route("/supabase")
def test_supabase():
    try:
        response = supabase.table("offices").select("*").limit(5).execute()

        return {
            "status": "Connected ✅",
            "rows": response.data
        }

    except Exception as e:
        return {
            "status": "Failed ❌",
            "error": str(e)
        }, 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
