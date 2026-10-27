"""Small independent Flask health/status surface for Janavani.

The Telegram webhook runtime is a separate service and is deliberately not
spawned from this process; failure of one interface must not stop the other.
"""
from flask import Flask

from core.config import Config
from database.supabase import supabase

app = Flask(__name__)


@app.route("/")
def home():
    """Return a minimal service landing page."""
    return """
    <h1>🇮🇳 Janavani</h1>
    <h2>Citizen Governance Platform</h2>
    <p>Web service is running independently.</p>
    <ul><li><a href="/health">Health Check</a></li></ul>
    """


@app.route("/health")
def health():
    """Report process liveness and whether Supabase is configured."""
    return {
        "status": "healthy",
        "database": "configured" if supabase else "not configured",
    }


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=Config.PORT, debug=False)
