from telegram import Update
from telegram.ext import ContextTypes

from conversation.state import set_state
from conversation.session import get_session
from conversation.constants import WAITING_FOR_FORMAT

from conversation.steps.format import show_format_buttons


async def handle_identity(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id
    session = get_session(user_id)

    session["identity_mode"] = "anonymous"

    set_state(user_id, WAITING_FOR_FORMAT)

    await update.message.reply_text("✅ Identity: Anonymous")

    # 🔥 SHOW BUTTONS
    await show_format_buttons(update)