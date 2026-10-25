"""Telegram webhook runtime; domain behavior stays in existing handlers/capabilities."""
from __future__ import annotations

import asyncio
import hmac
import json
import logging
import os
import re
from contextlib import asynccontextmanager
from typing import Any, AsyncIterator
from urllib.parse import urlsplit

from fastapi import FastAPI, Header, HTTPException, Request
from telegram import Update
from telegram.ext import Application

from src.bot_telegram import (
    _start_ephemeral_issue_cleanup,
    _stop_ephemeral_issue_cleanup,
    build_application,
)
from src.commands.catalogue import telegram_bot_commands
from src.storage.repositories.postgres_telegram_inbox import PostgresTelegramInbox
from src.web.telegram_inbox_worker import _renew_lease, run_inbox_worker

logger = logging.getLogger(__name__)

MAX_WEBHOOK_BODY_BYTES = 1_048_576


def _required_setting(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"{name} must be configured for Telegram webhook mode")
    return value


def create_webhook_app(*, application: Application | None = None, inbox: Any | None = None) -> FastAPI:
    """Build the webhook; production accepts updates only after durable inbox commit."""
    injected_application, injected_inbox = application is not None, inbox is not None
    inline_failed_updates: set[int] = set()

    async def record_inline_handler_error(update: object, context: Any) -> None:
        update_id = getattr(update, "update_id", None)
        if isinstance(update_id, int):
            inline_failed_updates.add(update_id)
        # Deliberately log only the Telegram update ID and exception, never the payload.
        logger.error(
            "Telegram inline webhook handler failed for update_id=%s error_type=%s",
            update_id,
            type(context.error).__name__,
        )

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        if injected_application:
            app.state.telegram_application = application
            app.state.webhook_secret = os.getenv("TELEGRAM_WEBHOOK_SECRET", "test-secret")
            app.state.inline_failed_updates = inline_failed_updates
            application.add_error_handler(record_inline_handler_error)
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
                application.remove_error_handler(record_inline_handler_error)
            return

        token, webhook_url = _required_setting("TELEGRAM_BOT_TOKEN"), _required_setting("TELEGRAM_WEBHOOK_URL")
        secret, dsn = _required_setting("TELEGRAM_WEBHOOK_SECRET"), _required_setting("JANAVANI_TELEGRAM_INBOX_DSN")
        if not re.fullmatch(r"[A-Za-z0-9_-]{32,256}", secret):
            raise RuntimeError("TELEGRAM_WEBHOOK_SECRET must be 32-256 URL-safe characters")
        parsed = urlsplit(webhook_url)
        if (parsed.scheme != "https" or not parsed.netloc or parsed.path != "/telegram/webhook"
                or parsed.query or parsed.fragment or parsed.username or parsed.password):
            raise RuntimeError("TELEGRAM_WEBHOOK_URL must be HTTPS and end in /telegram/webhook")

        bot_app, durable_inbox = build_application(token=token), PostgresTelegramInbox(dsn=dsn)
        app.state.inline_failed_updates = inline_failed_updates
        bot_app.add_error_handler(record_inline_handler_error)
        await bot_app.initialize()
        await bot_app.start()
        await bot_app.bot.set_my_commands(telegram_bot_commands())
        await bot_app.bot.set_webhook(url=webhook_url, secret_token=secret,
                                      allowed_updates=Update.ALL_TYPES, drop_pending_updates=False)
        _start_ephemeral_issue_cleanup(bot_app)
        app.state.telegram_application, app.state.telegram_inbox = bot_app, durable_inbox
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
            bot_app.remove_error_handler(record_inline_handler_error)

    app = FastAPI(title="Janavani Telegram Webhook", version="1.1.0", docs_url=None, redoc_url=None, lifespan=lifespan)
    app.state.inline_failed_updates = inline_failed_updates
    if injected_application:
        app.state.telegram_application = application
        app.state.webhook_secret = os.getenv("TELEGRAM_WEBHOOK_SECRET", "test-secret")
        if injected_inbox:
            app.state.telegram_inbox = inbox

    @app.get("/liveness")
    async def liveness() -> dict[str, str]:
        return {"status": "alive", "surface": "telegram-webhook"}

    @app.post("/telegram/webhook", status_code=202)
    async def telegram_webhook(request: Request, telegram_secret: str | None = Header(
        default=None, alias="X-Telegram-Bot-Api-Secret-Token"
    )) -> dict[str, str]:
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
            # Test-only compatibility: production startup always requires a durable inbox.
            # This branch only feeds an injected in-memory test application.
            try:
                await bot_app.update_queue.put(update)
            except Exception as exc:
                raise HTTPException(
                    status_code=503,
                    detail="Telegram update could not be accepted; retry delivery",
                ) from exc
            return {"status": "accepted"}

        try:
            receipt = await asyncio.to_thread(durable_inbox.claim_update, update_id)
        except Exception as exc:
            raise HTTPException(
                status_code=503,
                detail="Telegram update could not be claimed; retry delivery",
            ) from exc

        receipt_status = receipt["status"]
        if receipt_status in {"processed", "dead_letter"}:
            # Telegram may redeliver after the response is lost. A terminal receipt
            # prevents repeating the handler after successful completion.
            return {"status": "accepted"}
        if receipt_status != "claimed":
            # Busy receipts or the legacy payload queue must not be acknowledged:
            # Telegram should retry until the active/legacy worker finishes.
            raise HTTPException(
                status_code=503,
                detail="Telegram update is not yet ready for processing; retry delivery",
            )

        attempts = int(receipt["attempts"])
        failed_updates = request.app.state.inline_failed_updates
        failed_updates.discard(update_id)
        dispatch = asyncio.create_task(bot_app.process_update(update))
        lease = asyncio.create_task(_renew_lease(durable_inbox, update_id, attempts))
        try:
            done, _ = await asyncio.wait(
                {dispatch, lease}, return_when=asyncio.FIRST_COMPLETED
            )
            if lease in done:
                dispatch.cancel()
                await asyncio.gather(dispatch, return_exceptions=True)
                raise RuntimeError("telegram_inbox_lease_lost")
            await dispatch
            if update_id in failed_updates:
                raise RuntimeError("telegram_handler_failed")
            await asyncio.to_thread(
                durable_inbox.mark_processed,
                update_id,
                attempts=attempts,
            )
        except Exception as exc:
            if not dispatch.done():
                dispatch.cancel()
            try:
                await asyncio.to_thread(
                    durable_inbox.retry_or_dead_letter,
                    update_id,
                    attempts=attempts,
                    error_code=type(exc).__name__,
                )
            except Exception:
                logger.error(
                    "Could not update retry state for Telegram update_id=%s error_type=%s",
                    update_id,
                    type(exc).__name__,
                )
            raise HTTPException(
                status_code=503,
                detail="Telegram update could not be completed; retry delivery",
            ) from exc
        finally:
            lease.cancel()
            await asyncio.gather(lease, dispatch, return_exceptions=True)
        return {"status": "accepted"}

    return app


app = create_webhook_app()
