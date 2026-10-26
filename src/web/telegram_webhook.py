"""Webhook-only Telegram adapter for the canonical JanaVani bot application.

This module deliberately does not register polling. It translates Telegram HTTP
updates into the existing application handlers composed by src.bot_telegram.
"""
from __future__ import annotations

import hmac
import json
import os
from contextlib import asynccontextmanager
from typing import Any, AsyncIterator

from fastapi import APIRouter, HTTPException, Request
from telegram import Update
from telegram.ext import Application

from src.bot_telegram import build_application

router = APIRouter(prefix="/telegram", tags=["Telegram"])
_MAX_UPDATE_BYTES = 1024 * 1024


def _expected_secret() -> str:
    return os.environ.get("TELEGRAM_WEBHOOK_SECRET", "").strip()


@asynccontextmanager
async def telegram_application_lifespan(app: Any) -> AsyncIterator[None]:
    """Initialise the existing bot handlers without starting Telegram polling."""
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    secret = _expected_secret()
    if not token or not secret:
        app.state.telegram_application = None
        yield
        return

    telegram_app: Application = build_application(token=token)
    await telegram_app.initialize()
    await telegram_app.start()
    app.state.telegram_application = telegram_app
    try:
        yield
    finally:
        app.state.telegram_application = None
        await telegram_app.stop()
        await telegram_app.shutdown()


@router.post("/webhook")
async def receive_telegram_update(request: Request) -> dict[str, bool]:
    """Validate and dispatch a Telegram update; never invoke polling."""
    expected = _expected_secret()
    supplied = request.headers.get("X-Telegram-Bot-Api-Secret-Token", "")
    if not expected or not supplied or not hmac.compare_digest(supplied, expected):
        raise HTTPException(status_code=403, detail="Invalid webhook secret")

    length = request.headers.get("content-length")
    if length:
        try:
            if int(length) > _MAX_UPDATE_BYTES:
                raise HTTPException(status_code=413, detail="Update payload too large")
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid Content-Length") from None

    telegram_app: Application | None = getattr(
        request.app.state, "telegram_application", None
    )
    if telegram_app is None:
        raise HTTPException(status_code=503, detail="Telegram adapter is not configured")

    body = await request.body()
    if len(body) > _MAX_UPDATE_BYTES:
        raise HTTPException(status_code=413, detail="Update payload too large")
    try:
        payload = json.loads(body)
        if not isinstance(payload, dict):
            raise ValueError("Telegram update must be a JSON object")
        update = Update.de_json(payload, telegram_app.bot)
        if update is None:
            raise ValueError("Telegram update is empty")
    except (json.JSONDecodeError, ValueError, TypeError):
        raise HTTPException(status_code=400, detail="Invalid Telegram update") from None

    # Await dispatch so Telegram receives success only after the current handler
    # chain completes. Domain-side idempotency is still required for durable
    # protection against retries and must be enforced by the capability/storage
    # boundary before this adapter is considered production-hardened.
    await telegram_app.process_update(update)
    return {"ok": True}
