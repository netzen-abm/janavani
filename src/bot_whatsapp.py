"""Independent WhatsApp webhook surface."""
from __future__ import annotations

import os

from flask import Flask

from src.adapters.meta_graph_client import send_meta_message
from src.adapters.meta_webhook_security import register_meta_webhook_routes

app = Flask(__name__)
TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_ID = os.getenv("WHATSAPP_PHONE_ID")
VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN")
APP_SECRET = os.getenv("WHATSAPP_APP_SECRET") or os.getenv("META_APP_SECRET")

register_meta_webhook_routes(
    app,
    channel="whatsapp",
    verify_token=VERIFY_TOKEN,
    app_secret=APP_SECRET,
)


def send_whatsapp(recipient: str, text: str) -> bool:
    """Send a WhatsApp text message through the Meta Graph API."""
    payload = {
        "messaging_product": "whatsapp",
        "to": recipient,
        "type": "text",
        "text": {"body": text},
    }
    return send_meta_message(PHONE_ID or "", TOKEN, payload)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")))
