from telegram import Update
from telegram.ext import ContextTypes

from conversation.session import get_session
from conversation.state import set_state

from conversation.constants import (
    WAITING_FOR_GENERATE,
)


async def handle_identity(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """
    Handles the citizen's identity preference.

    Identity Modes

    1 - Anonymous

    2 - Name Only

    3 - Full Identity
    """

    user_id = update.effective_user.id

    session = get_session(user_id)

    choice = update.message.text.strip()

    if choice == "1":

        session["identity_mode"] = "anonymous"

    elif choice == "2":

        session["identity_mode"] = "name"

    elif choice == "3":

        session["identity_mode"] = "full"

    else:

        await update.message.reply_text(
            "Please reply with 1, 2 or 3."
        )

        return

    set_state(
        user_id,
        WAITING_FOR_GENERATE
    )

    await update.message.reply_text(
f"""
✅ Identity Mode Selected

{session["identity_mode"]}

Generating your document...
"""
    )
