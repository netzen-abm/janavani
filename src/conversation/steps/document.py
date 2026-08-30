from telegram import Update
from telegram.ext import ContextTypes

from conversation.session import get_session
from conversation.state import set_state
from conversation.constants import WAITING_FOR_DISTRICT


async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Select the civic action type; document generation happens later."""
    user_id = update.effective_user.id
    session = get_session(user_id)
    choice = update.message.text.strip()

    document_types = {"1": "Complaint", "2": "RTI"}
    if choice not in document_types:
        await update.message.reply_text("Please reply with 1 or 2.")
        return

    session["document"] = document_types[choice]
    await update.message.reply_text(
        f"""✅ Civic action selected

{session['document']}

Now enter your District.

Example:
Ernakulam
Kozhikode
Kannur"""
    )
    set_state(user_id, WAITING_FOR_DISTRICT)
