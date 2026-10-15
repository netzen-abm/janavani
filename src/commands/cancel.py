"""User-controlled cancellation and deletion of transient Telegram workflow state."""
from telegram import Update
from telegram.ext import ContextTypes

from conversation.session import clear_session
from conversation.state import user_states


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Discard the caller's in-memory workflow and any short-lived draft content."""
    user = update.effective_user
    message = update.effective_message
    if user is None or message is None:
        return
    clear_session(user.id)
    user_states.pop(user.id, None)
    await message.reply_text(
        "Your current Janavani workflow was cancelled and its in-memory session cleared. "
        "This does not delete messages already stored by Telegram or documents you downloaded."
    )
