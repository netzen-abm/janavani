import os
from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return """
    <h1>🇮🇳 Janavani</h1>
    <p>Citizen Governance Platform</p>
    <p>Status: Running ✅</p>
    """

@app.route("/health")
def health():
    return {
        "status": "ok",
        "service": "Janavani",
        "version": "0.1"
    }

@app.route("/webhook")
def webhook():
    return "Telegram webhook endpoint (coming next)", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
