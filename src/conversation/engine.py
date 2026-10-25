"""Telegram conversation dispatcher.

Transport/state routing belongs here; civic business semantics remain in
canonical capabilities. Errors are converted to safe user-facing responses
without leaking internal exception details.
"""
from __future__ import annotations

import logging

from conversation.constants import COMPLETED, WAITING_FOR_ISSUE
from conversation.session import clear_session, get_ephemeral_issue
from conversation.state import get_state, user_states
from conversation.state_registry import get_handler

logger = logging.getLogger(__name__)


async def run_step(update, context):
    chat = getattr(update, "effective_chat", None)
    if chat is None or chat.type != "private":
        query = getattr(update, "callback_query", None)
        if query is not None:
            await query.answer()
        message = getattr(update, "effective_message", None)
        if message is not None:
            await message.reply_text(
                "For privacy, Janavani complaint workflows are available only in a "
                "private chat with the bot. Open a private chat and use /complaint."
            )
        return

    if update.callback_query:
        user_id = update.callback_query.from_user.id
    elif update.effective_user:
        user_id = update.effective_user.id
    else:
        return

    state = get_state(user_id)

    # Conversation state is process-local, while citizen-authored issue text has
    # a deliberate 15-minute TTL. Never continue a later step without its text.
    if state not in {"NEW", WAITING_FOR_ISSUE, COMPLETED} and not get_ephemeral_issue(user_id):
        clear_session(user_id)
        user_states.pop(user_id, None)
        logger.info("telegram_workflow_expired state=%s", state)
        if update.callback_query:
            await update.callback_query.answer()
        message = getattr(update, "effective_message", None)
        if message is not None:
            await message.reply_text(
                "Your temporary issue description expired or was lost after a restart. "
                "For privacy, Janavani did not save it. Use /complaint to restart."
            )
        return

    if state == "NEW":
        if update.callback_query:
            await update.callback_query.answer()
            message = getattr(update, "effective_message", None)
            if message is not None:
                await message.reply_text(
                    "That button belongs to an earlier workflow. Use /complaint "
                    "to start a new one; expired issue text is not recoverable."
                )
            return
        if update.message:
            # The welcome flow promises free-text intake: dispatch the first
            # plain-text message to the same issue handler as /complaint.
            state = WAITING_FOR_ISSUE
        else:
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
    except Exception as exc:
        logger.error(
            "telegram_workflow_failure state=%s error_type=%s",
            state,
            type(exc).__name__,
        )
        if update.message:
            await update.message.reply_text(
                "⚠️ Janavani is temporarily unable to complete this step. "
                "Your existing Case is not being reported as completed."
            )
