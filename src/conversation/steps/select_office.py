from telegram import Update
from telegram.ext import ContextTypes

from conversation.session import get_session
from conversation.state import set_state

from services.office_service import find_offices


async def handle_select_office(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    user_id = update.effective_user.id
    location = update.message.text.strip()

    session = get_session(user_id)
    department = session.get("department", "")

    offices = find_offices(department, location)

    # --------------------------------------
    # ❌ NO OFFICE FOUND
    # --------------------------------------

    if not offices:

        await update.message.reply_text(
            "⚠️ No exact office found.\n\n"
            "You can still continue:\n\n"
            "1 → Enter office manually\n"
            "2 → Continue without office\n\n"
            "Reply with 1 or 2."
        )

        session["office"] = None

        set_state(
            user_id,
            "WAITING_FOR_OFFICE_FALLBACK"
        )

        return

    # --------------------------------------
    # ✅ OFFICE FOUND
    # --------------------------------------

    session["offices"] = offices

    msg = "🏢 Found offices:\n\n"

    for i, office in enumerate(offices, start=1):
        msg += f"{i}. {office['name']} ({office['city']})\n"

    msg += "\nReply with office number."

    await update.message.reply_text(msg)

    set_state(user_id, "WAITING_FOR_OFFICE_SELECTION")