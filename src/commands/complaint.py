from telegram import Update
from telegram.ext import ContextTypes

from conversation.state import set_state
from conversation.session import clear_ephemeral_issue, clear_session
from conversation.constants import WAITING_FOR_ISSUE


async def complaint(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user is None or update.message is None:
        return
    user_id = update.effective_user.id
    clear_ephemeral_issue(user_id)
    clear_session(user_id)

    # 🎯 Start flow
    set_state(user_id, WAITING_FOR_ISSUE)

    await update.message.reply_text(
        """📝 Please describe your issue.

Example:
My road has been broken for 3 months
"""
    )