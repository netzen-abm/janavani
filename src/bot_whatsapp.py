"""Independent WhatsApp webhook surface.

Provider transport lives here. Shared Janavani capabilities must not require
Telegram, Web, Messenger, or another client runtime.
"""

from __future__ import annotations

import os

import requests
from flask import Flask, jsonify, request

app = Flask(__name__)
TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_ID = os.getenv("WHATSAPP_PHONE_ID")

_session = requests.Session()
_session.mount("https://", requests.adapters.HTTPAdapter(pool_maxsize=10))


def send_whatsapp(recipient: str, text: str) -> bool:
    """Send a text message directly through the WhatsApp provider API."""
    if not TOKEN or not PHONE_ID:
        return False

    url = f"https://graph.facebook.com/v19.0/{PHONE_ID}/messages"
    headers = {"Authorization": f"Bearer {TOKEN}"}
    payload = {
        "messaging_product": "whatsapp",
        "to": recipient,
        "type": "text",
        "text": {"body": text},
    }

    try:
        response = _session.post(url, headers=headers, json=payload, timeout=(2, 5))
        response.raise_for_status()
    except requests.RequestException:
        return False
    return True


@app.get("/webhook")
def verify_webhook():
    """Handle Meta webhook verification."""
    challenge = request.args.get("hub.challenge")
    return challenge or "", 200 if challenge else 400


@app.post("/webhook")
def webhook():
    """Accept WhatsApp events without depending on another surface."""
    payload = request.get_json(silent=True) or {}
    # Provider parsing and capability dispatch are separate concerns.
    return jsonify({"status": "accepted", "received": bool(payload)}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")))
