from telegram import Update
from telegram.ext import ContextTypes

from conversation.session import get_session
from conversation.state import set_state
from conversation.constants import WAITING_FOR_PREVIEW

from conversation.steps.preview import handle_preview  # 🔥 IMPORTANT


async def handle_office_manual(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    session = get_session(user_id)

    text = update.message.text.strip()

    try:
        name, address = text.split(",", 1)
    except ValueError:
        await update.message.reply_text(
            """
❌ Invalid format.

Please use:
Office Name, Address

Example:
Village Office Kannur, Near Collectorate
"""
        )
        return

    office = {
        "name": name.strip(),
        "address": address.strip(),
        "district": session.get("district", "Unknown"),
    }

    session["office"] = office

    await update.message.reply_text(
        f"""
✅ Office recorded

🏢 {office["name"]}
📍 {office["address"]}
"""
    )

    # ✅ Move state
    set_state(user_id, WAITING_FOR_PREVIEW)

    # 🔥 CRITICAL FIX: trigger next step immediately
    await handle_preview(update, context)