"""Independent Messenger webhook surface."""
from __future__ import annotations

import os

from flask import Flask

from src.adapters.meta_graph_client import send_meta_message
from src.adapters.meta_webhook_security import register_meta_webhook_routes

app = Flask(__name__)
TOKEN = os.getenv("MESSENGER_TOKEN")
PAGE_ID = os.getenv("MESSENGER_PAGE_ID") or os.getenv("MESSENGER_PHONE_ID")
VERIFY_TOKEN = os.getenv("MESSENGER_VERIFY_TOKEN")
APP_SECRET = os.getenv("MESSENGER_APP_SECRET") or os.getenv("META_APP_SECRET")

register_meta_webhook_routes(
    app,
    channel="messenger",
    verify_token=VERIFY_TOKEN,
    app_secret=APP_SECRET,
)


def send_messenger(recipient_id: str, text: str) -> bool:
    """Send a Messenger text message through the Meta Graph API."""
    payload = {
        "messaging_type": "RESPONSE",
        "recipient": {"id": recipient_id},
        "message": {"text": text},
    }
    return send_meta_message(PAGE_ID or "", TOKEN, payload)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")))
