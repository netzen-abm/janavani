from telegram import Update
from telegram.ext import ContextTypes

from conversation.session import get_session
from conversation.state import set_state
from conversation.constants import WAITING_FOR_ADDRESS


async def handle_name(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id
    session = get_session(user_id)

    # ✅ Save name
    session["citizen_name"] = update.message.text.strip()

    # ✅ ALWAYS go to address (FIXED FLOW)
    set_state(user_id, WAITING_FOR_ADDRESS)

    await update.message.reply_text(
        "📍 Please enter your address:"
    )