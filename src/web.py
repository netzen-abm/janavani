from flask import Flask

from core.config import Config
from database.supabase import supabase

app = Flask(__name__)


# ---------------------------------
# Home
# ---------------------------------
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


# ---------------------------------
# Health Check
# ---------------------------------
@app.route("/health")
def health():

    return {
        "status": "healthy",
        "database": "connected" if supabase else "not configured"
    }


# ---------------------------------
# Supabase Test
# ---------------------------------
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


# ---------------------------------
# Run Flask
# ---------------------------------
if __name__ == "__main__":

    print("=" * 50)
    print("Starting Janavani Web Server")
    print("=" * 50)

    app.run(
        host="0.0.0.0",
        port=Config.PORT,
        debug=False
    )
