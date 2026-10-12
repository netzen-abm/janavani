"""Background processor for durably accepted Telegram webhook updates."""
from __future__ import annotations

import asyncio
import logging
from typing import Any

from telegram import Update
from telegram.ext import Application

from src.storage.repositories.postgres_telegram_inbox import PostgresTelegramInbox

logger = logging.getLogger(__name__)


async def _renew_lease(inbox: PostgresTelegramInbox, update_id: int, attempts: int) -> None:
    """Keep the claim alive; returning means ownership was lost or cannot be proven."""
    while True:
        await asyncio.sleep(30)
        try:
            owned = await asyncio.to_thread(inbox.heartbeat, update_id, attempts=attempts)
            if owned is False:
                raise RuntimeError("Telegram inbox processing lease was lost")
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.exception("Telegram inbox lease renewal failed for update_id=%s", update_id)
            return


async def run_inbox_worker(
    application: Application, inbox: PostgresTelegramInbox, *, poll_seconds: float = 0.5
) -> None:
    """Dispatch accepted updates; stop dispatch when lease ownership is lost."""
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
            attempts = int(item["attempts"])
            lease = asyncio.create_task(_renew_lease(inbox, update_id, attempts))
            dispatch = asyncio.create_task(_dispatch(application, item, failed_updates))
            try:
                done, _ = await asyncio.wait(
                    {dispatch, lease}, return_when=asyncio.FIRST_COMPLETED
                )
                if lease in done:
                    dispatch.cancel()
                    try:
                        await dispatch
                    except asyncio.CancelledError:
                        pass
                    raise RuntimeError("telegram_inbox_lease_lost")
                await dispatch
                await asyncio.to_thread(inbox.mark_processed, update_id, attempts=attempts)
            except asyncio.CancelledError:
                dispatch.cancel()
                raise
            except Exception as exc:
                logger.exception("Telegram inbox processing failed for update_id=%s", update_id)
                try:
                    await asyncio.to_thread(
                        inbox.retry_or_dead_letter, update_id,
                        attempts=attempts, error_code=type(exc).__name__,
                    )
                except Exception:
                    # A reclaimed claim must not mutate the newer worker's state.
                    logger.exception("Telegram inbox retry state update failed for update_id=%s", update_id)
            finally:
                lease.cancel()
                if not dispatch.done():
                    dispatch.cancel()
                for task in (lease, dispatch):
                    try:
                        await task
                    except asyncio.CancelledError:
                        pass
    finally:
        application.remove_error_handler(record_handler_error)


async def _dispatch(application: Application, item: dict[str, Any], failed_updates: set[int]) -> None:
    update_id = int(item["update_id"])
    update = Update.de_json(item["payload"], application.bot)
    if update is None:
        raise ValueError("invalid_update")
    failed_updates.discard(update_id)
    await application.process_update(update)
    # python-telegram-bot routes handler errors through registered error handlers.
    if update_id in failed_updates:
        raise RuntimeError("telegram_handler_failed")
