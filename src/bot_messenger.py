"""Independent Messenger webhook surface.

Transport-specific behavior stays here; Janavani capabilities should be
implemented in shared services and invoked through stable interfaces.
"""

from __future__ import annotations

import os

from flask import Flask, jsonify, request
import requests

app = Flask(__name__)
TOKEN = os.getenv("MESSENGER_TOKEN")
PAGE_ID = os.getenv("MESSENGER_PAGE_ID") or os.getenv("MESSENGER_PHONE_ID")

_session = requests.Session()
_session.mount("https://", requests.adapters.HTTPAdapter(pool_maxsize=10))


def send_messenger(recipient_id: str, text: str) -> bool:
    """Send a text message without depending on another Janavani surface."""
    if not TOKEN or not PAGE_ID:
        return False

    url = f"https://graph.facebook.com/v19.0/{PAGE_ID}/messages"
    headers = {"Authorization": f"Bearer {TOKEN}"}
    payload = {
        "messaging_type": "RESPONSE",
        "recipient": {"id": recipient_id},
        "message": {"text": text},
    }

    try:
        response = _session.post(url, headers=headers, json=payload, timeout=(2, 5))
        response.raise_for_status()
    except requests.RequestException:
        return False
    return True


@app.get("/webhook")
def verify_webhook():
    """Handle provider webhook verification."""
    challenge = request.args.get("hub.challenge")
    return challenge or "", 200 if challenge else 400


@app.post("/webhook")
def webhook():
    """Accept Messenger events without assuming a WhatsApp runtime exists."""
    payload = request.get_json(silent=True) or {}
    # Provider-specific event interpretation remains intentionally small here.
    # Capability dispatch will be added through the shared messaging contract.
    return jsonify({"status": "accepted", "received": bool(payload)}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")))
