from telegram import Update
from telegram.ext import ContextTypes

from conversation.state import set_state
from conversation.session import get_session
from conversation.constants import WAITING_FOR_ADDRESS, WAITING_FOR_FORMAT
from conversation.steps.format import show_format_buttons


async def handle_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Acknowledge name entry without retaining the name in server-side session state."""
    user_id = update.effective_user.id
    session = get_session(user_id)

    if update.message is None or not update.message.text.strip():
        await update.message.reply_text("Please enter a name or choose a different identity mode.")
        return

    # The name remains in the current Telegram update only. Do not copy it into
    # the Janavani session or any persistent repository.
    if session.get("identity_mode") == "full":
        set_state(user_id, WAITING_FOR_ADDRESS)
        await update.message.reply_text(
            "📍 If an address is required for the selected destination, enter it now. "
            "It will be used only for this requested action and is not retained by Janavani."
        )
    else:
        set_state(user_id, WAITING_FOR_FORMAT)
        await show_format_buttons(update)
