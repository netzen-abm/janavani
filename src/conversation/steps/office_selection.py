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

    session["office"] = offices[choice - 1]
    set_state(user_id, WAITING_FOR_PREVIEW)
    await handle_preview(update, context)
