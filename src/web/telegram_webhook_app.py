"""Telegram webhook adapter; encrypted durable delivery stays in the inbox/worker boundary."""
from __future__ import annotations

import asyncio
import hmac
import json
import logging
import os
from contextlib import asynccontextmanager
from typing import Any, AsyncIterator

from fastapi import FastAPI, Header, HTTPException, Request
from telegram import Update
from telegram.ext import Application

from src.bot_telegram import (
    _start_ephemeral_issue_cleanup,
    _stop_ephemeral_issue_cleanup,
    build_application,
)
from src.commands.catalogue import telegram_bot_commands
from src.config.runtime import validate_runtime_configuration
from src.storage.repositories.postgres_telegram_inbox import PostgresTelegramInbox
from src.web.telegram_inbox_worker import run_inbox_worker
from src.web.telegram_webhook_config import load_telegram_webhook_settings

logger = logging.getLogger(__name__)
MAX_WEBHOOK_BODY_BYTES = 1_048_576

def create_webhook_app(*, application: Application | None = None, inbox: Any | None = None) -> FastAPI:
    """Create an endpoint that acknowledges only updates durably encrypted in PostgreSQL."""
    injected_application, injected_inbox = application is not None, inbox is not None

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        if injected_application:
            app.state.telegram_application = application
            app.state.webhook_secret = os.getenv("TELEGRAM_WEBHOOK_SECRET", "test-secret")
            if injected_inbox:
                app.state.telegram_inbox = inbox
                app.state.inbox_worker = asyncio.create_task(run_inbox_worker(application, inbox))
            try:
                yield
            finally:
                worker = getattr(app.state, "inbox_worker", None)
                if worker:
                    worker.cancel()
                    try:
                        await worker
                    except asyncio.CancelledError:
                        pass
            return

        settings = load_telegram_webhook_settings()
        token = settings.bot_token
        webhook_url = settings.webhook_url
        secret = settings.secret
        dsn = settings.inbox_dsn
        encryption_keys = list(settings.encryption_keys)

        validate_runtime_configuration()
        bot_app = build_application(token=token)
        durable_inbox = PostgresTelegramInbox(dsn=dsn, encryption_keys=encryption_keys)
        # Migrate any historical plaintext rows to ciphertext before registering the webhook.
        await asyncio.to_thread(durable_inbox.secure_legacy_payloads)
        await bot_app.initialize()
        await bot_app.start()
        await bot_app.bot.set_my_commands(telegram_bot_commands())
        await bot_app.bot.set_webhook(
            url=webhook_url,
            secret_token=secret,
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=False,
        )
        _start_ephemeral_issue_cleanup(bot_app)
        app.state.telegram_application = bot_app
        app.state.telegram_inbox = durable_inbox
        app.state.webhook_secret = secret
        worker = asyncio.create_task(run_inbox_worker(bot_app, durable_inbox))
        app.state.inbox_worker = worker
        try:
            yield
        finally:
            worker.cancel()
            try:
                await worker
            except asyncio.CancelledError:
                pass
            await _stop_ephemeral_issue_cleanup(bot_app)
            await bot_app.stop()
            await bot_app.shutdown()

    app = FastAPI(
        title="Janavani Telegram Webhook",
        version="1.2.0",
        docs_url=None,
        redoc_url=None,
        lifespan=lifespan,
    )
    if injected_application:
        app.state.telegram_application = application
        app.state.webhook_secret = os.getenv("TELEGRAM_WEBHOOK_SECRET", "test-secret")
        if injected_inbox:
            app.state.telegram_inbox = inbox

    @app.get("/liveness")
    async def liveness() -> dict[str, str]:
        return {"status": "alive", "surface": "telegram-webhook"}

    @app.post("/telegram/webhook", status_code=202)
    async def telegram_webhook(
        request: Request,
        telegram_secret: str | None = Header(
            default=None, alias="X-Telegram-Bot-Api-Secret-Token"
        ),
    ) -> dict[str, str]:
        expected = getattr(request.app.state, "webhook_secret", None)
        if not expected or not telegram_secret or not hmac.compare_digest(expected, telegram_secret):
            raise HTTPException(status_code=403, detail="Invalid webhook secret")
        declared = request.headers.get("content-length")
        if declared is not None:
            try:
                length = int(declared)
            except ValueError as exc:
                raise HTTPException(status_code=400, detail="Invalid Content-Length") from exc
            if length < 0:
                raise HTTPException(status_code=400, detail="Invalid Content-Length")
            if length > MAX_WEBHOOK_BODY_BYTES:
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
        update_id = payload.get("update_id")
        if isinstance(update_id, bool) or not isinstance(update_id, int) or update_id < 0:
            raise HTTPException(status_code=400, detail="Update must include a valid update_id")
        bot_app: Application = request.app.state.telegram_application
        try:
            update = Update.de_json(payload, bot_app.bot)
        except Exception as exc:
            raise HTTPException(status_code=400, detail="Invalid Telegram update") from exc
        if update is None or update.update_id != update_id:
            raise HTTPException(status_code=400, detail="Invalid Telegram update")

        durable_inbox = getattr(request.app.state, "telegram_inbox", None)
        if durable_inbox is None:
            # Never acknowledge an update that has not been durably accepted.
            # Test fixtures may omit the inbox for liveness-only checks, but a
            # webhook delivery without durable storage must remain retryable.
            raise HTTPException(
                status_code=503,
                detail="Telegram durable inbox is unavailable; retry delivery",
            )

        try:
            await asyncio.to_thread(durable_inbox.accept_encrypted, update_id, payload)
        except Exception as exc:
            logger.error(
                "Telegram webhook durable acceptance failed for update_id=%s error_type=%s",
                update_id,
                type(exc).__name__,
            )
            raise HTTPException(
                status_code=503,
                detail="Telegram update could not be durably accepted; retry delivery",
            ) from exc
        return {"status": "accepted"}

    return app

app = create_webhook_app()
