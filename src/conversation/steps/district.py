from telegram import Update
from telegram.ext import ContextTypes

from conversation.session import get_session
from conversation.state import set_state

from conversation.constants import (
    WAITING_FOR_OFFICE,
    WAITING_FOR_OFFICE_MANUAL
)

from services.office_service import find_offices


async def handle_district(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id
    user_input = update.message.text.strip()

    session = get_session(user_id)

    # Save district input
    session["district"] = user_input

    # Search offices
    offices = find_offices(
        session["department"],
        user_input
    )

    # --------------------------------------
    # ❌ NO MATCH FOUND
    # --------------------------------------
    if offices is None:

        await update.message.reply_text(
            "❌ No office found for this location.\n\n"
            "✍️ You can enter manually (Example: Kannur Municipality)"
        )

        session["manual_location"] = user_input
        return

    # --------------------------------------
    # ✅ MATCH FOUND
    # --------------------------------------
    session["offices"] = offices

    await update.message.reply_text(
        f"✅ Found {len(offices)} office(s)"
    )

# --------------------------------------
# ❌ NO MATCH FOUND
# --------------------------------------

if offices is None:

    await update.message.reply_text(
        "❌ No office found for this location.\n\n"
        "✍️ You can enter manually (Example: Kannur Municipality / Local Office)"
    )

    # Save manual input
    session["manual_location"] = user_input

    return

# --------------------------------------
# ✅ MATCH FOUND
# --------------------------------------

session["offices"] = offices

await update.message.reply_text(
    f"✅ Found {len(offices)} office(s)"
)

    session["offices"] = offices

    # 🔴 FIX 1: correct variable + indentation
    if not offices:

        await update.message.reply_text(
            f"""
⚠️ No matching office found for:

{district.title()}

You can enter details manually.

Please type in this format:

Office Name, Address

Example:
Village Office Kannur, Near Collectorate
"""
        )

        set_state(user_id, WAITING_FOR_OFFICE_MANUAL)
        return

    # Build office list
    office_list = ""

    for index, office in enumerate(offices, start=1):
        office_list += f"{index}. {office['office_name']}\n"

    # Move to next step
    set_state(user_id, WAITING_FOR_OFFICE)

    await update.message.reply_text(
        f"""
🏢 I found these offices:

{office_list}

Reply with the office number.
"""
    )