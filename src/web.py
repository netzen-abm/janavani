"""Legacy Flask web entrypoint kept isolated from the canonical FastAPI app.

This module must not start or own any other access surface. Telegram runs as an
independent process/runtime. New deployment paths should use
``src.web.canonical_app:app``.
"""

from flask import Flask

from core.config import Config
from database.supabase import supabase

app = Flask(__name__)


@app.route("/")
def home():
    return """
    <h1>🇮🇳 Janavani</h1>
    <h2>Citizen Governance Platform</h2>

    <p>✅ Legacy Flask compatibility surface</p>

    <ul>
        <li><a href="/health">Health Check</a></li>
        <li><a href="/supabase">Supabase Test</a></li>
    </ul>

    <p>Canonical API: <code>src.web.canonical_app:app</code></p>
    """


@app.route("/health")
def health():
    return {
        "status": "healthy",
        "database": "connected" if supabase else "not configured",
        "runtime": "legacy-compatibility",
        "canonical_runtime": "src.web.canonical_app:app",
    }


@app.route("/supabase")
def supabase_test():
    if supabase is None:
        return {
            "status": "error",
            "message": "Supabase is not configured.",
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
            "rows": response.data,
        }
    except Exception as exc:
        return {
            "status": "failed",
            "error": str(exc),
        }, 500


if __name__ == "__main__":
    print("Starting Janavani legacy Flask compatibility surface")
    print("Telegram is an independent runtime and will not be spawned by Web.")
    print("Canonical production API: src.web.canonical_app:app")
    app.run(host="0.0.0.0", port=Config.PORT, debug=False)
