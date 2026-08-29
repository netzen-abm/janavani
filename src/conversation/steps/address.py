from telegram import Update
from telegram.ext import ContextTypes

from conversation.session import get_session
from conversation.state import set_state
from conversation.constants import WAITING_FOR_PREVIEW


async def handle_address(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id
    session = get_session(user_id)

    # ✅ Save address
    session["address"] = update.message.text.strip()

    # ✅ Move to preview (FIXED)
    await update.message.reply_text("Preparing preview...")

    set_state(user_id, WAITING_FOR_PREVIEW)