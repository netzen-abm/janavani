from telegram import Update
from telegram.ext import ContextTypes

from conversation.session import get_session
from conversation.state import set_state
from conversation.constants import WAITING_FOR_DISTRICT


async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id

    session = get_session(user_id)

    choice = update.message.text.strip()

    if choice == "1":

        session["document"] = "Complaint"

    elif choice == "2":

        session["document"] = "RTI"

    else:

        await update.message.reply_text(
            "Please reply with 1 or 2."
        )
        return

    set_state(
        user_id,
        WAITING_FOR_DISTRICT
    )

    await update.message.reply_text(
f"""
✅ Document Selected

{session["document"]}

Now enter your District.

Example

Ernakulam
Kozhikode
Kannur
"""
    )
