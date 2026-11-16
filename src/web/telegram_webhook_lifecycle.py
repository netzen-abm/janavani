"""Retryable production startup for the webhook and its durable worker."""
from __future__ import annotations

import asyncio
import logging
from typing import Any

from src.bot_telegram import _start_ephemeral_issue_cleanup, _stop_ephemeral_issue_cleanup
from src.commands.catalogue import telegram_bot_commands
from src.web.telegram_inbox_worker import run_inbox_worker
from telegram import Update

logger = logging.getLogger(__name__)
STARTUP_RETRY_INITIAL_SECONDS = 1.0
STARTUP_RETRY_MAX_SECONDS = 30.0


async def stop_task(task: asyncio.Task[Any] | None, *, purpose: str = "inbox shutdown worker") -> None:
    if task is None:
        return
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass
    except Exception as exc:
        logger.error("Telegram %s failure type=%s", purpose, type(exc).__name__)


async def start_webhook_runtime(
    app: Any, *, bot_app: Any, inbox: Any, webhook_url: str, secret: str
) -> None:
    """Keep ingress retryable until migration, bot setup and worker startup succeed."""
    delay = STARTUP_RETRY_INITIAL_SECONDS
    while True:
        try:
            # Legacy plaintext rows must be secured before Telegram delivery is enabled.
            await asyncio.to_thread(inbox.secure_legacy_payloads)
            if not app.state.telegram_initialized:
                await bot_app.initialize()
                app.state.telegram_initialized = True
            if not app.state.telegram_started:
                await bot_app.start()
                app.state.telegram_started = True
            await bot_app.bot.set_my_commands(telegram_bot_commands())
            await bot_app.bot.set_webhook(
                url=webhook_url,
                secret_token=secret,
                allowed_updates=Update.ALL_TYPES,
                drop_pending_updates=False,
            )
            _start_ephemeral_issue_cleanup(bot_app)
            app.state.inbox_worker = asyncio.create_task(run_inbox_worker(bot_app, inbox))
            app.state.runtime_ready = True
            logger.info("Telegram webhook runtime ready")
            return
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            app.state.runtime_ready = False
            logger.warning(
                "Telegram webhook startup incomplete; retrying in %.1fs error_type=%s",
                delay,
                type(exc).__name__,
            )
            if app.state.telegram_started:
                try:
                    await bot_app.stop()
                    app.state.telegram_started = False
                except Exception as stop_exc:
                    logger.warning("Telegram startup cleanup stop failed type=%s", type(stop_exc).__name__)
            if app.state.telegram_initialized and not app.state.telegram_started:
                try:
                    await bot_app.shutdown()
                    app.state.telegram_initialized = False
                except Exception as shutdown_exc:
                    logger.warning(
                        "Telegram startup cleanup shutdown failed type=%s",
                        type(shutdown_exc).__name__,
                    )
            await asyncio.sleep(delay)
            delay = min(delay * 2, STARTUP_RETRY_MAX_SECONDS)


async def stop_webhook_runtime(app: Any, bot_app: Any) -> None:
    app.state.runtime_ready = False
    await stop_task(getattr(app.state, "inbox_worker", None))
    try:
        await _stop_ephemeral_issue_cleanup(bot_app)
    except Exception as exc:
        logger.error("Telegram cleanup shutdown failure type=%s", type(exc).__name__)
    if app.state.telegram_started:
        try:
            await bot_app.stop()
            app.state.telegram_started = False
        except Exception as exc:
            logger.error("Telegram application stop failure type=%s", type(exc).__name__)
    if app.state.telegram_initialized and not app.state.telegram_started:
        try:
            await bot_app.shutdown()
            app.state.telegram_initialized = False
        except Exception as exc:
            logger.error("Telegram application shutdown failure type=%s", type(exc).__name__)
