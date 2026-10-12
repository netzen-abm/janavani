"""Background processor for durably accepted Telegram webhook updates."""
from __future__ import annotations

import asyncio
import logging
from typing import Any

from telegram import Update
from telegram.ext import Application

from src.storage.repositories.postgres_telegram_inbox import PostgresTelegramInbox

logger = logging.getLogger(__name__)


async def _renew_lease(inbox: PostgresTelegramInbox, update_id: int) -> None:
    while True:
        await asyncio.sleep(30)
        try:
            await asyncio.to_thread(inbox.heartbeat, update_id)
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.exception("Telegram inbox lease renewal failed for update_id=%s", update_id)


async def run_inbox_worker(
    application: Application, inbox: PostgresTelegramInbox, *, poll_seconds: float = 0.5
) -> None:
    """Dispatch accepted updates; observe PTB handler errors for bounded retry."""
    failed_updates: set[int] = set()

    async def record_handler_error(update: object, context: Any) -> None:
        update_id = getattr(update, "update_id", None)
        if isinstance(update_id, int):
            failed_updates.add(update_id)
        logger.error("Telegram handler raised an error for update_id=%s", update_id,
                     exc_info=context.error)

    application.add_error_handler(record_handler_error)
    try:
        while True:
            item = await asyncio.to_thread(inbox.claim_next)
            if item is None:
                await asyncio.sleep(poll_seconds)
                continue
            update_id = int(item["update_id"])
            lease = asyncio.create_task(_renew_lease(inbox, update_id))
            try:
                update = Update.de_json(item["payload"], application.bot)
                if update is None:
                    raise ValueError("invalid_update")
                failed_updates.discard(update_id)
                await application.process_update(update)
                # python-telegram-bot reports handler exceptions through its error
                # handlers instead of propagating them from process_update().
                if update_id in failed_updates:
                    raise RuntimeError("telegram_handler_failed")
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                logger.exception("Telegram inbox processing failed for update_id=%s", update_id)
                try:
                    await asyncio.to_thread(
                        inbox.retry_or_dead_letter, update_id,
                        attempts=int(item["attempts"]), error_code=type(exc).__name__,
                    )
                except Exception:
                    logger.exception("Telegram inbox retry state update failed for update_id=%s", update_id)
                continue
            else:
                try:
                    await asyncio.to_thread(inbox.mark_processed, update_id)
                except Exception:
                    # Leave the row processing; lease expiry makes it recoverable.
                    logger.exception("Telegram inbox completion mark failed for update_id=%s", update_id)
            finally:
                lease.cancel()
                try:
                    await lease
                except asyncio.CancelledError:
                    pass
    finally:
        application.remove_error_handler(record_handler_error)
