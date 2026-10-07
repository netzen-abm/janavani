from telegram import Update
from telegram.ext import ContextTypes

from conversation.session import get_session
from conversation.state import set_state
from conversation.constants import WAITING_FOR_FORMAT


async def handle_address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Consume an address transiently; never store it in Janavani session state."""
    user_id = update.effective_user.id
    session = get_session(user_id)

    if update.message is None or not update.message.text.strip():
        await update.message.reply_text("Please enter an address or return to the previous step.")
        return

    # The address remains only in the current transport update. It is not copied
    # into the session, repository, logs or telemetry by this handler.
    set_state(user_id, WAITING_FOR_FORMAT)

    await update.message.reply_text(
        "📄 Choose format:\n1️⃣ PDF\n2️⃣ DOCX"
    )
