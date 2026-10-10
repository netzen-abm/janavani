"""Telegram office-selection interaction.

Discovery and selection are separate responsibilities: discovery populates
candidate offices; this handler selects one candidate and advances the flow.
"""
from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes

from conversation.constants import WAITING_FOR_PREVIEW
from conversation.session import get_session
from conversation.steps.preview import handle_preview
from conversation.state import set_state
from src.capabilities.authority import AuthorityCapability
from src.commands.shared_case_capability import create_case_for_telegram_session


async def handle_office_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message is None or update.effective_user is None:
        return

    user_id = update.effective_user.id
    session = get_session(user_id)
    offices = session.get("offices", [])

    try:
        choice = int(update.message.text.strip())
    except (TypeError, ValueError):
        await update.message.reply_text("Please enter a valid office number.")
        return

    if choice < 1 or choice > len(offices):
        await update.message.reply_text("Invalid office number.")
        return

    selected = offices[choice - 1]
    authority_capability: AuthorityCapability | None = (
        context.application.bot_data.get("authority_capability")
    )
    if authority_capability is None:
        await update.message.reply_text("Authority verification is temporarily unavailable.")
        return
    try:
        authority_capability.require_verified_destination(str(selected["id"]))
        session["office"] = selected
        create_case_for_telegram_session(
            user_id=user_id, context=context, session=session,
            related_office_id=str(selected["id"]),
        )
    except (LookupError, ValueError, PermissionError):
        await update.message.reply_text(
            "That office is not verified in Janavani's canonical directory. "
            "Please choose another verified office."
        )
        return
    set_state(user_id, WAITING_FOR_PREVIEW)
    await handle_preview(update, context)
