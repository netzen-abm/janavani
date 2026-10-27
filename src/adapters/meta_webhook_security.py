"""Shared verification and route registration for Meta webhook ingress."""
from __future__ import annotations

import hashlib
import hmac
import logging
from typing import Any, Callable, Optional

from flask import Flask, jsonify, request

logger = logging.getLogger("janavani.adapters.meta_webhook_security")


def verify_meta_webhook_challenge(
    mode: Optional[str],
    supplied_token: Optional[str],
    challenge: Optional[str],
    expected_token: Optional[str],
) -> tuple[str, int]:
    """Validate Meta's subscription handshake using the configured verify token."""
    if not expected_token or mode != "subscribe" or not supplied_token or not challenge:
        return "", 403
    if not hmac.compare_digest(supplied_token, expected_token):
        return "", 403
    return challenge, 200


def is_valid_meta_signature(
    raw_body: bytes,
    signature_header: Optional[str],
    app_secret: Optional[str],
) -> bool:
    """Validate X-Hub-Signature-256 over the raw request bytes."""
    if not app_secret or not signature_header or not signature_header.startswith("sha256="):
        return False
    expected = "sha256=" + hmac.new(
        app_secret.encode("utf-8"), raw_body, hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(signature_header, expected)


def register_meta_webhook_routes(
    app: Flask,
    *,
    channel: str,
    verify_token: Optional[str],
    app_secret: Optional[str],
    event_dispatcher: Optional[Callable[[dict[str, Any]], bool]] = None,
) -> None:
    """Register shared secure routes on an independently deployed Meta app.

    The event dispatcher must return True only after the event is durably
    accepted for processing. With no dispatcher, valid deliveries receive 503
    rather than a false 200 acknowledgement and silent data loss.
    """
    @app.get("/webhook", endpoint=f"{channel}_verify_webhook")
    def verify_webhook():
        """Verify the subscription challenge."""
        challenge, status = verify_meta_webhook_challenge(
            request.args.get("hub.mode"),
            request.args.get("hub.verify_token"),
            request.args.get("hub.challenge"),
            verify_token,
        )
        return challenge, status

    @app.post("/webhook", endpoint=f"{channel}_receive_webhook")
    def receive_webhook():
        """Authenticate incoming events before parsing or dispatching them."""
        raw_body = request.get_data(cache=True)
        if not is_valid_meta_signature(
            raw_body, request.headers.get("X-Hub-Signature-256"), app_secret
        ):
            return jsonify({"error": "invalid_signature"}), 401

        payload = request.get_json(silent=True)
        if not isinstance(payload, dict):
            return jsonify({"error": "invalid_payload"}), 400

        if event_dispatcher is None:
            return jsonify({"error": "event_dispatch_unavailable"}), 503

        try:
            accepted = event_dispatcher(payload)
        except Exception:  # Provider events must not leak internal details.
            logger.warning("Meta webhook dispatcher failed for channel %s", channel)
            return jsonify({"error": "event_dispatch_unavailable"}), 503

        if not accepted:
            return jsonify({"error": "event_dispatch_unavailable"}), 503
        return jsonify({"status": "accepted"}), 200
