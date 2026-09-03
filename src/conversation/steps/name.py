from telegram import Update
from telegram.ext import ContextTypes

from conversation.state import set_state
from conversation.session import get_session
from conversation.constants import WAITING_FOR_ADDRESS, WAITING_FOR_FORMAT

from conversation.steps.format import show_format_buttons


async def handle_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    session = get_session(user_id)

    name = update.message.text.strip()
    session["name"] = name
    session["citizen_name"] = name

    if session.get("identity_mode") == "full":
        set_state(user_id, WAITING_FOR_ADDRESS)
        await update.message.reply_text("📍 Now enter your address:")
    else:
        set_state(user_id, WAITING_FOR_FORMAT)
        await show_format_buttons(update)
