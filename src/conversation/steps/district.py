from telegram import Update
from telegram.ext import ContextTypes

from conversation.session import get_session
from conversation.state import set_state

from conversation.constants import WAITING_FOR_OFFICE

from src.services.office_service import find_offices


async def handle_district(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id

    session = get_session(user_id)

    session["district"] = update.message.text.strip()

    offices = find_offices(

        session["issue"],

        session["district"]

    )

    session["offices"] = offices

    if len(offices) == 0:

        await update.message.reply_text(
f"""
District recorded

{session["district"]}

⚠️ No matching office found.
"""
        )

        return

    office_list = ""

    for index, office in enumerate(offices, start=1):

        office_list += f"{index}. {office['office_name']}\n"

    set_state(

        user_id,

        WAITING_FOR_OFFICE

    )

    await update.message.reply_text(
f"""
I found these offices.

{office_list}

Reply with the office number.
"""
    )
