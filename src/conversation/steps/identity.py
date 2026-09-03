from telegram import Update
from telegram.ext import ContextTypes

from conversation.state import set_state
from conversation.session import get_session
from conversation.constants import WAITING_FOR_FORMAT

from conversation.steps.format import show_format_buttons


async def handle_identity(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()
    session = get_session(user_id)

    if text not in ["1", "2", "3", "4"]:
        await update.message.reply_text(
            "❌ Invalid choice.\n\nReply with 1, 2, 3, or 4."
        )
        return

    identity_map = {
        "1": "anonymous",
        "2": "name_only",
        "3": "address_only",
        "4": "full",
    }
    identity_labels = {
        "1": "Anonymous",
        "2": "Name Only",
        "3": "Address Only",
        "4": "Full Details",
    }

    session["identity_mode"] = identity_map[text]
    set_state(user_id, WAITING_FOR_FORMAT)

    await update.message.reply_text(
        f"✅ Identity: {identity_labels[text]}"
    )
    await show_format_buttons(update)
