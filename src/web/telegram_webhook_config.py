"""Validated environment configuration for the Telegram webhook runtime."""
from __future__ import annotations

import os
import re
from dataclasses import dataclass
from urllib.parse import urlsplit


@dataclass(frozen=True, slots=True)
class TelegramWebhookSettings:
    bot_token: str
    webhook_url: str
    secret: str
    inbox_dsn: str
    encryption_keys: tuple[str, ...]


def load_telegram_webhook_settings() -> TelegramWebhookSettings:
    """Fail closed unless the public webhook has durable encrypted inbox settings."""
    def required(name: str) -> str:
        value = os.getenv(name, "").strip()
        if not value:
            raise RuntimeError(f"{name} must be configured for Telegram webhook mode")
        return value

    token = required("TELEGRAM_BOT_TOKEN")
    webhook_url = required("TELEGRAM_WEBHOOK_URL")
    secret = required("TELEGRAM_WEBHOOK_SECRET")
    inbox_dsn = required("JANAVANI_TELEGRAM_INBOX_DSN")
    raw_keys = required("JANAVANI_TELEGRAM_INBOX_ENCRYPTION_KEYS")
    keys = tuple(value.strip() for value in raw_keys.split(",") if value.strip())
    if not keys:
        raise RuntimeError("JANAVANI_TELEGRAM_INBOX_ENCRYPTION_KEYS must contain at least one key")
    if not re.fullmatch(r"[A-Za-z0-9_-]{32,256}", secret):
        raise RuntimeError("TELEGRAM_WEBHOOK_SECRET must be 32-256 URL-safe characters")
    parsed = urlsplit(webhook_url)
    if (
        parsed.scheme != "https"
        or not parsed.netloc
        or parsed.path != "/telegram/webhook"
        or parsed.query
        or parsed.fragment
        or parsed.username
        or parsed.password
    ):
        raise RuntimeError("TELEGRAM_WEBHOOK_URL must be HTTPS and end in /telegram/webhook")
    return TelegramWebhookSettings(token, webhook_url, secret, inbox_dsn, keys)
