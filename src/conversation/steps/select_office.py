from telegram import Update
from telegram.ext import ContextTypes

from conversation.session import get_session
from conversation.state import set_state

from conversation.constants import (
    WAITING_FOR_OFFICE,
    WAITING_FOR_OFFICE_FALLBACK,
    WAITING_FOR_IDENTITY
)

from services.office_service import find_offices


async def handle_select_office(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    user_id = update.effective_user.id
    session = get_session(user_id)

    # --------------------------------------
    # 📍 GET CONTEXT
    # --------------------------------------
    district = session.get("district", "")
    department = session.get("department", "")

    # --------------------------------------
    # 🔍 FIND OFFICES (SMART)
    # --------------------------------------
    offices = find_offices(district, department)

    # --------------------------------------
    # ❌ NO OFFICE → FALLBACK
    # --------------------------------------
    if not offices:
        await update.message.reply_text(
            "⚠️ No office found for your district.\n\n"
            "You can still continue:\n\n"
            "1 → Enter office manually\n"
            "2 → Continue without office\n\n"
            "Reply with 1 or 2."
        )

        session["office"] = None
        set_state(user_id, WAITING_FOR_OFFICE_FALLBACK)
        return

    # --------------------------------------
    # 🧠 AUTO-SELECT IF SINGLE RESULT
    # --------------------------------------
    if len(offices) == 1:
        office = offices[0]
        session["office"] = office

        name = office.get("name", "Unknown Office")
        city = office.get("city", "")

        await update.message.reply_text(
            f"✅ Auto-selected office:\n{name} {f'({city})' if city else ''}"
        )

        set_state(user_id, WAITING_FOR_IDENTITY)
        return

    # --------------------------------------
    # 📋 MULTIPLE OPTIONS → SHOW LIST
    # --------------------------------------
    session["offices"] = offices

    msg = "🏢 Found offices:\n\n"

    for i, office in enumerate(offices, start=1):
        name = office.get("name", "Unknown")
        city = office.get("city", "")
        msg += f"{i}. {name} {f'({city})' if city else ''}\n"

    msg += "\nReply with office number."

    await update.message.reply_text(msg)

    # --------------------------------------
    # ⏳ WAIT FOR USER SELECTION
    # --------------------------------------
    set_state(user_id, WAITING_FOR_OFFICE)