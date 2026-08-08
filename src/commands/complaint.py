from telegram import Update
from telegram.ext import ContextTypes

from conversation.state import set_state
from conversation.constants import WAITING_FOR_ISSUE


async def complaint(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    # 🎯 Start flow
    set_state(user_id, WAITING_FOR_ISSUE)

    await update.message.reply_text(
        """📝 Please describe your issue.

Example:
My road has been broken for 3 months
"""
    )