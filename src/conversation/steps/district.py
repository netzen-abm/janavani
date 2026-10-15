"""Capture a citizen-entered district without falsely asserting verification."""
from telegram import Update
from telegram.ext import ContextTypes

from conversation.session import get_session
from conversation.state import set_state
from conversation.constants import WAITING_FOR_OFFICE


async def handle_district(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user is None or update.message is None:
        return

    user_id = update.effective_user.id
    user_input = (update.message.text or "").strip()

    # Reject unusable input, but do not pretend a format check verifies jurisdiction.
    if len(user_input) < 2 or len(user_input) > 100:
        await update.message.reply_text(
            "Please enter a district name between 2 and 100 characters. "
            "You can also use /cancel to stop."
        )
        return

    if not any(character.isalpha() for character in user_input):
        await update.message.reply_text(
            "Please enter a district name using letters, not only numbers or symbols."
        )
        return

    session = get_session(user_id)
    session["district"] = user_input

    await update.message.reply_text(
        f"""📍 District entered: {user_input.title()}

This entry has not yet been verified against official jurisdiction data.
Now enter your area / city:
Example: Aluva, Kochi
"""
    )
    set_state(user_id, WAITING_FOR_OFFICE)
