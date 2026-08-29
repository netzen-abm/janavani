from telegram import Update
from telegram.ext import ContextTypes

from conversation.session import get_session
from conversation.state import set_state

from conversation.constants import (
    WAITING_FOR_OFFICE_MANUAL,
    WAITING_FOR_IDENTITY
)


async def handle_office_fallback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    user_id = update.effective_user.id
    session = get_session(user_id)

    choice = update.message.text.strip()

    # --------------------------------------
    # OPTION 1 → MANUAL OFFICE ENTRY
    # --------------------------------------
    if choice == "1":
        await update.message.reply_text(
            "Please enter office details in this format:\n\n"
            "Office Name, City"
        )

        set_state(user_id, WAITING_FOR_OFFICE_MANUAL)
        return

    # --------------------------------------
    # OPTION 2 → CONTINUE WITHOUT OFFICE
    # --------------------------------------
    elif choice == "2":

        session["office"] = {
            "name": "Not specified",
            "city": ""
        }

        await update.message.reply_text(
            "Continuing without selecting an office.\n\n"
            "Please choose identity option:\n"
            "1. Anonymous\n"
            "2. Name"
        )

        # ✅ GO TO IDENTITY (FIXED)
        set_state(user_id, WAITING_FOR_IDENTITY)
        return

    # --------------------------------------
    # INVALID INPUT
    # --------------------------------------
    else:
        await update.message.reply_text("Please reply with 1 or 2.")
        return