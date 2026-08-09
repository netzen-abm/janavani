from telegram import Update
from telegram.ext import ContextTypes

from conversation.session import get_session
from conversation.state import set_state
from conversation.constants import WAITING_FOR_PREVIEW

from conversation.steps.preview import handle_preview


async def handle_office_manual(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    user_id = update.effective_user.id

    session = get_session(user_id)

    text = update.message.text.strip()

    # --------------------------------------
    # 🧾 PARSE INPUT
    # --------------------------------------

    try:
        name, address = text.split(",", 1)

    except ValueError:

        await update.message.reply_text(
            "❌ Invalid format.\n\n"
            "Please use:\n"
            "Office Name, Address\n\n"
            "Example:\n"
            "Village Office Kannur, Near Collectorate"
        )
        return

    # --------------------------------------
    # 🏢 SAVE OFFICE
    # --------------------------------------

    office = {
        "id": "manual",
        "name": name.strip(),
        "address": address.strip(),
        "district": session.get("district", "Unknown"),
    }

    session["office"] = office

    # --------------------------------------
    # ✅ CONFIRM TO USER
    # --------------------------------------

    await update.message.reply_text(
        f"✅ Office recorded\n\n"
        f"🏢 {office['name']}\n"
        f"📍 {office['address']}"
    )

    # --------------------------------------
    # 🔄 MOVE TO PREVIEW
    # --------------------------------------

    set_state(user_id, WAITING_FOR_PREVIEW)

    # 🔥 TRIGGER NEXT STEP
    await handle_preview(update, context)