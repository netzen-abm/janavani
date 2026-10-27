"""Independent WhatsApp webhook surface.

Message construction and webhook transport are provider-specific; common Meta
HTTP mechanics and authenticity checks are delegated to small shared helpers.
"""
from __future__ import annotations

import os

from flask import Flask, jsonify, request

from src.adapters.meta_graph_client import send_meta_message
from src.adapters.meta_webhook_security import (
    is_valid_meta_signature,
    verify_meta_webhook_challenge,
)

app = Flask(__name__)
TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_ID = os.getenv("WHATSAPP_PHONE_ID")
VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN")
APP_SECRET = os.getenv("WHATSAPP_APP_SECRET") or os.getenv("META_APP_SECRET")


def send_whatsapp(recipient: str, text: str) -> bool:
    """Send a WhatsApp text message through the Meta Graph API."""
    payload = {
        "messaging_product": "whatsapp",
        "to": recipient,
        "type": "text",
        "text": {"body": text},
    }
    return send_meta_message(PHONE_ID or "", TOKEN, payload)


@app.get("/webhook")
def verify_webhook():
    """Verify the configured Meta subscription handshake."""
    challenge, status = verify_meta_webhook_challenge(
        request.args.get("hub.mode"),
        request.args.get("hub.verify_token"),
        request.args.get("hub.challenge"),
        VERIFY_TOKEN,
    )
    return challenge, status


@app.post("/webhook")
def webhook():
    """Reject unauthenticated deliveries and avoid acknowledging dropped events."""
    raw_body = request.get_data(cache=True)
    if not is_valid_meta_signature(
        raw_body, request.headers.get("X-Hub-Signature-256"), APP_SECRET
    ):
        return jsonify({"error": "invalid_signature"}), 401

    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({"error": "invalid_payload"}), 400

    # A durable event dispatcher is not wired yet. Ask Meta to retry instead
    # of replying 200 and silently discarding a real citizen message.
    return jsonify({"error": "event_dispatch_unavailable"}), 503


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")))
