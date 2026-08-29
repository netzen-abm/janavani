from telegram import Update
from telegram.ext import ContextTypes

from conversation.session import get_session
from conversation.state import set_state
from conversation.constants import WAITING_FOR_PREVIEW


async def handle_office_manual(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    user_id = update.effective_user.id
    session = get_session(user_id)

    text = update.message.text.strip()

    # --------------------------------------
    # 🧠 FLEXIBLE PARSING (IMPROVED)
    # --------------------------------------
    parts = [p.strip() for p in text.split(",")]

    office = {
        "id": "manual",
        "name": parts[0] if parts else "Not specified",
        "address": parts[1] if len(parts) > 1 else "",
        "district": session.get("district", "Unknown"),
    }

    session["office"] = office

    # --------------------------------------
    # ✅ CONFIRM TO USER
    # --------------------------------------
    name = office["name"]
    address = office["address"]

    msg = f"✅ Office recorded\n\n🏢 {name}"
    if address:
        msg += f"\n📍 {address}"

    await update.message.reply_text(msg)

    # --------------------------------------
    # 🔄 MOVE TO PREVIEW (STATE-DRIVEN)
    # --------------------------------------
    set_state(user_id, WAITING_FOR_PREVIEW)