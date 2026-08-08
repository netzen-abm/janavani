from telegram import Update
from telegram.ext import ContextTypes

from conversation.session import get_session
from conversation.state import set_state
from conversation.constants import WAITING_FOR_FORMAT


async def handle_address(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id
    session = get_session(user_id)

    session["address"] = update.message.text.strip()

    set_state(user_id, WAITING_FOR_FORMAT)

    await update.message.reply_text(
        "📄 Choose format:\n1️⃣ PDF\n2️⃣ DOCX"
    )