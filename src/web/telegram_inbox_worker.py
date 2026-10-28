"""Durably process encrypted Telegram update payloads with bounded retries."""
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
        except Exception as exc:
            logger.error(
                "Telegram inbox lease renewal failed for update_id=%s error_type=%s",
                update_id,
                type(exc).__name__,
            )
            return


async def run_inbox_worker(
    application: Application, inbox: PostgresTelegramInbox, *, poll_seconds: float = 0.5
) -> None:
    """Process encrypted Telegram updates and survive transient inbox-claim failures."""
    failed_updates: set[int] = set()
    claim_failures = 0

    async def record_handler_error(update: object, context: Any) -> None:
        update_id = getattr(update, "update_id", None)
        if isinstance(update_id, int):
            failed_updates.add(update_id)
        logger.error(
            "Telegram handler failed for update_id=%s error_type=%s",
            update_id,
            type(context.error).__name__,
        )

    application.add_error_handler(record_handler_error)
    try:
        while True:
            try:
                item = await asyncio.to_thread(inbox.claim_next)
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                # A transient database error must not terminate the durable inbox
                # worker. Retry with capped exponential backoff and never log DSNs,
                # payloads, or exception messages that could contain secrets.
                claim_failures = min(claim_failures + 1, 7)
                retry_delay = min(max(poll_seconds, 0.5) * (2 ** (claim_failures - 1)), 30.0)
                logger.error(
                    "Telegram inbox claim failed; retrying in %.1fs error_type=%s",
                    retry_delay,
                    type(exc).__name__,
                )
                await asyncio.sleep(retry_delay)
                continue
            claim_failures = 0
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
                    await asyncio.gather(dispatch, return_exceptions=True)
                    raise RuntimeError("telegram_inbox_lease_lost")
                await dispatch
                await asyncio.to_thread(inbox.mark_processed, update_id, attempts=attempts)
            except asyncio.CancelledError:
                dispatch.cancel()
                raise
            except Exception as exc:
                logger.error(
                    "Telegram inbox processing failed for update_id=%s error_type=%s",
                    update_id,
                    type(exc).__name__,
                )
                try:
                    await asyncio.to_thread(
                        inbox.retry_or_dead_letter, update_id,
                        attempts=attempts, error_code=type(exc).__name__,
                    )
                except Exception:
                    # A reclaimed claim must not mutate the newer worker's state.
                    logger.error(
                        "Telegram inbox retry state update failed for update_id=%s error_type=%s",
                        update_id,
                        type(exc).__name__,
                    )
            finally:
                lease.cancel()
                if not dispatch.done():
                    dispatch.cancel()
                # Gather consumes child-task outcomes without swallowing cancellation
                # requested on this worker itself. A broad CancelledError handler here
                # can otherwise turn shutdown into an endless polling loop.
                await asyncio.gather(lease, dispatch, return_exceptions=True)
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
