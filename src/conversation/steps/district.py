from telegram import Update
from telegram.ext import ContextTypes

from conversation.session import get_session
from conversation.state import set_state

from conversation.constants import WAITING_FOR_OFFICE


async def handle_district(update: Update, context: ContextTypes.DEFAULT_TYPE):

    # --------------------------------------
    # 🔐 USER INPUT
    # --------------------------------------

    user_id = update.effective_user.id
    user_input = update.message.text.strip()

    session = get_session(user_id)

    # Save district
    session["district"] = user_input

    # --------------------------------------
    # ➡️ MOVE TO NEXT STEP (IMPORTANT)
    # --------------------------------------

    await update.message.reply_text(
        f"""
📍 District selected: {user_input.title()}

Now enter your area / city:
Example: Aluva, Kochi
"""
    )

    set_state(user_id, WAITING_FOR_OFFICE)