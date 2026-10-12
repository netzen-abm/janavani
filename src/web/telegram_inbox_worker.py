"""Background processor for durably accepted Telegram webhook updates."""
from __future__ import annotations

import asyncio
import logging
from typing import Any

from telegram import Update
from telegram.ext import Application

from src.storage.repositories.postgres_telegram_inbox import PostgresTelegramInbox

logger = logging.getLogger(__name__)


async def run_inbox_worker(
    application: Application, inbox: PostgresTelegramInbox, *, poll_seconds: float = 0.5
) -> None:
    """Process durable inbox entries until cancelled; never acknowledge in-memory work."""
    while True:
        item = await asyncio.to_thread(inbox.claim_next)
        if item is None:
            await asyncio.sleep(poll_seconds)
            continue
        update_id = int(item["update_id"])
        try:
            update = Update.de_json(item["payload"], application.bot)
            if update is None:
                raise ValueError("invalid_update")
            await application.process_update(update)
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            logger.exception("Telegram inbox processing failed for update_id=%s", update_id)
            try:
                await asyncio.to_thread(
                    inbox.retry_or_dead_letter,
                    update_id,
                    attempts=int(item["attempts"]),
                    error_code=type(exc).__name__,
                )
            except Exception:
                logger.exception("Telegram inbox retry state update failed for update_id=%s", update_id)
            continue
        await asyncio.to_thread(inbox.mark_processed, update_id)
