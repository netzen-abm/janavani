from telegram import Update
from telegram.ext import ContextTypes

from conversation.state import set_state
from conversation.session import get_session

from conversation.constants import (
    WAITING_FOR_NAME,
    WAITING_FOR_ADDRESS
)


async def handle_identity(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id
    text = update.message.text.strip()

    session = get_session(user_id)

    # --------------------------------------
    # VALIDATE INPUT
    # --------------------------------------

    if text not in ["1", "2", "3", "4"]:
        await update.message.reply_text(
            "❌ Invalid choice.\n\nReply with 1, 2, 3, or 4."
        )
        return

    # --------------------------------------
    # MAP USER CHOICE
    # --------------------------------------

    identity_map = {
        "1": "anonymous",
        "2": "name_only",
        "3": "address_only",
        "4": "full"
    }

    identity_labels = {
        "1": "Anonymous",
        "2": "Name Only",
        "3": "Address Only",
        "4": "Full Details"
    }

    selected_mode = identity_map[text]
    selected_label = identity_labels[text]

    # SAVE
    session["identity_mode"] = selected_mode

    # --------------------------------------
    # ROUTING (FIXED)
    # --------------------------------------

    # ✅ Anonymous → skip name → go to address
    if selected_mode == "anonymous":
        session["citizen_name"] = "Anonymous"

        set_state(user_id, WAITING_FOR_ADDRESS)

        await update.message.reply_text(
            "✅ Identity: Anonymous\n\n📍 Enter your address:"
        )
        return

    # ✅ Address Only → skip name → go to address
    if selected_mode == "address_only":
        session["citizen_name"] = "Not provided"

        set_state(user_id, WAITING_FOR_ADDRESS)

        await update.message.reply_text(
            "✅ Identity: Address Only\n\n📍 Enter your address:"
        )
        return

    # ✅ Name Only / Full → go to name
    if selected_mode in ["name_only", "full"]:
        set_state(user_id, WAITING_FOR_NAME)

        await update.message.reply_text(
            f"✅ Identity: {selected_label}\n\n👤 Enter your name:"
        )
        return