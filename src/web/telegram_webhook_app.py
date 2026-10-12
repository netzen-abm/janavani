""""Dedicated Telegram webhook runtime for the free-tier Render web service.

Telegram updates are authenticated with Telegram's webhook secret header and
queued into the existing python-telegram-bot application. Business logic remains
in the existing handlers and shared capabilities.
"""
from __future__ import annotations

import hmac
import json
import os
import re
from contextlib import asynccontextmanager
from typing import AsyncIterator
from urllib.parse import urlsplit

from fastapi import FastAPI, Header, HTTPException, Request
from telegram import BotCommand, Update
from telegram.ext import Application

from src.bot_telegram import build_application


# Telegram updates should be small JSON envelopes. Bound ingress memory use even
# when a caller omits or lies about Content-Length.
MAX_WEBHOOK_BODY_BYTES = 1_048_576


def _required_setting(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"{name} must be configured for Telegram webhook mode")
    return value


def _webhook_commands() -> list[BotCommand]:
    return [
        BotCommand("start", "Start Janavani"),
        BotCommand("help", "View help and available commands"),
        BotCommand("complaint", "Start a test complaint workflow"),
        BotCommand("search", "Find public-service information"),
        BotCommand("check", "Check a case you own"),
        BotCommand("pair", "Start account pairing"),
        BotCommand("privacy", "Understand data handling"),
        BotCommand("cancel", "Clear the current in-memory workflow"),
        BotCommand("rate", "Share feedback"),
    ]


def create_webhook_app(*, application: Application | None = None) -> FastAPI:
    """Build a webhook app; injected applications allow transport tests."""

    injected_application = application is not None

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        if injected_application:
            app.state.telegram_application = application
            app.state.webhook_secret = os.getenv("TELEGRAM_WEBHOOK_SECRET", "test-secret")
            yield
            return

        token = _required_setting("TELEGRAM_BOT_TOKEN")
        webhook_url = _required_setting("TELEGRAM_WEBHOOK_URL")
        secret = _required_setting("TELEGRAM_WEBHOOK_SECRET")
        if not re.fullmatch(r"[A-Za-z0-9_-]{32,256}", secret):
            raise RuntimeError(
                "TELEGRAM_WEBHOOK_SECRET must be 32-256 characters using only "
                "letters, digits, underscores or hyphens"
            )
        parsed_webhook_url = urlsplit(webhook_url)
        if (
            parsed_webhook_url.scheme != "https"
            or not parsed_webhook_url.netloc
            or parsed_webhook_url.path != "/telegram/webhook"
            or parsed_webhook_url.query
            or parsed_webhook_url.fragment
            or parsed_webhook_url.username
            or parsed_webhook_url.password
        ):
            raise RuntimeError(
                "TELEGRAM_WEBHOOK_URL must be an HTTPS URL ending exactly in /telegram/webhook"
            )

        telegram_application = build_application(token=token)
        await telegram_application.initialize()
        await telegram_application.start()
        await telegram_application.bot.set_my_commands(_webhook_commands())
        await telegram_application.bot.set_webhook(
            url=webhook_url,
            secret_token=secret,
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=False,
        )
        app.state.telegram_application = telegram_application
        app.state.webhook_secret = secret
        try:
            yield
        finally:
            await telegram_application.stop()
            await telegram_application.shutdown()

    app = FastAPI(
        title="Janavani Telegram Webhook",
        version="1.0.0",
        docs_url=None,
        redoc_url=None,
        lifespan=lifespan,
    )

    if injected_application:
        # Test clients may not enter lifespan unless used as a context manager.
        # Populate injected transport dependencies at construction for deterministic tests.
        app.state.telegram_application = application
        app.state.webhook_secret = os.getenv("TELEGRAM_WEBHOOK_SECRET", "test-secret")

    @app.get("/liveness")
    async def liveness() -> dict[str, str]:
        return {"status": "alive", "surface": "telegram-webhook"}

    @app.post("/telegram/webhook", status_code=202)
    async def telegram_webhook(
        request: Request,
        telegram_secret: str | None = Header(
            default=None,
            alias="X-Telegram-Bot-Api-Secret-Token",
        ),
    ) -> dict[str, str]:
        expected = getattr(request.app.state, "webhook_secret", None)
        if not expected or not telegram_secret or not hmac.compare_digest(
            expected, telegram_secret
        ):
            raise HTTPException(status_code=403, detail="Invalid webhook secret")

        declared_length = request.headers.get("content-length")
        if declared_length is not None:
            try:
                parsed_length = int(declared_length)
            except ValueError as exc:
                raise HTTPException(status_code=400, detail="Invalid Content-Length") from exc
            if parsed_length < 0:
                raise HTTPException(status_code=400, detail="Invalid Content-Length")
            if parsed_length > MAX_WEBHOOK_BODY_BYTES:
                raise HTTPException(status_code=413, detail="Telegram update exceeds size limit")

        body = bytearray()
        async for chunk in request.stream():
            body.extend(chunk)
            if len(body) > MAX_WEBHOOK_BODY_BYTES:
                raise HTTPException(status_code=413, detail="Telegram update exceeds size limit")

        try:
            payload = json.loads(body)
        except (ValueError, UnicodeDecodeError) as exc:
            raise HTTPException(status_code=400, detail="Invalid JSON update") from exc
        if not isinstance(payload, dict):
            raise HTTPException(status_code=400, detail="Update must be a JSON object")

        telegram_application: Application = request.app.state.telegram_application
        try:
            update = Update.de_json(payload, telegram_application.bot)
        except Exception as exc:
            # Treat parser failures as invalid client input, not an unhandled 500.
            # Do not include the untrusted payload in the response or logs.
            raise HTTPException(status_code=400, detail="Invalid Telegram update") from exc
        if update is None:
            raise HTTPException(status_code=400, detail="Invalid Telegram update")
        try:
            await telegram_application.update_queue.put(update)
        except Exception as exc:
            # Non-2xx tells Telegram the update was not accepted so it can retry.
            # This does not make the in-memory queue durable across process crashes.
            raise HTTPException(
                status_code=503,
                detail="Telegram update could not be queued; retry delivery",
            ) from exc
        return {"status": "accepted"}

    return app


app = create_webhook_app()
