from telegram import Update
from telegram.ext import ContextTypes

from conversation.session import get_session
from conversation.state import set_state


async def handle_office_fallback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    user_id = update.effective_user.id
    text = update.message.text.strip()

    session = get_session(user_id)

    # --------------------------------------
    # OPTION 1 → MANUAL ENTRY
    # --------------------------------------
    if text == "1":

        await update.message.reply_text(
            "Please enter office details:\n\n"
            "Format:\n"
            "Office Name, City\n\n"
            "Example:\n"
            "Edathala Panchayat, Kochi"
        )

        set_state(user_id, "WAITING_FOR_MANUAL_OFFICE")
        return

    # --------------------------------------
    # OPTION 2 → CONTINUE WITHOUT OFFICE
    # --------------------------------------
    elif text == "2":

        session["office"] = {
            "id": "manual",
            "name": "Not Specified",
            "city": session.get("district", "Unknown")
        }

        await update.message.reply_text(
            "✅ Continuing without selecting office."
        )

        set_state(user_id, "SHOWING_PREVIEW")
        return

    # --------------------------------------
    # INVALID INPUT
    # --------------------------------------
    else:

        await update.message.reply_text(
            "❌ Invalid choice.\n"
            "Reply with 1 or 2."
        )