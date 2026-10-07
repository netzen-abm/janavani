"""Telegram conversation dispatcher.

Transport/state routing belongs here; civic business semantics remain in
canonical capabilities. Errors are converted to safe user-facing responses
without leaking internal exception details.
"""
from __future__ import annotations

import logging

from conversation.state import get_state
from conversation.state_registry import get_handler

logger = logging.getLogger(__name__)


async def run_step(update, context):
    if update.callback_query:
        user_id = update.callback_query.from_user.id
    elif update.effective_user:
        user_id = update.effective_user.id
    else:
        return

    state = get_state(user_id)

    if state == "NEW":
        if update.message:
            await update.message.reply_text(
                "👋 Welcome to Janavani. Use /complaint to begin, "
                "or describe your civic issue in your next message."
            )
        return

    handler = get_handler(state)
    if handler is None:
        logger.warning("telegram_unknown_conversation_state state=%s", state)
        if update.message:
            await update.message.reply_text(
                "⚠️ Your conversation state is no longer available. "
                "Please use /start to begin again."
            )
        return

    try:
        await handler(update, context)
    except (ValueError, LookupError, PermissionError) as exc:
        logger.info(
            "telegram_workflow_rejected state=%s error_type=%s",
            state,
            type(exc).__name__,
        )
        if update.message:
            await update.message.reply_text(
                "⚠️ I could not complete that step. "
                "Please review the information and try again."
            )
    except Exception:
        logger.exception("telegram_workflow_failure state=%s", state)
        if update.message:
            await update.message.reply_text(
                "⚠️ Janavani is temporarily unable to complete this step. "
                "Your existing Case is not being reported as completed."
            )
