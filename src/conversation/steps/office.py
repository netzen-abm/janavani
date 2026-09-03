from telegram import Update
from telegram.ext import ContextTypes

from conversation.session import get_session
from conversation.state import set_state

from conversation.constants import WAITING_FOR_PREVIEW


async def handle_office(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    session = get_session(user_id)
    offices = session.get("offices", [])

    try:
        choice = int(update.message.text.strip())
    except (TypeError, ValueError):
        await update.message.reply_text("Please enter a valid office number.")
        return

    if choice < 1 or choice > len(offices):
        await update.message.reply_text("Invalid office number.")
        return

    office = offices[choice - 1]
    session["office"] = office
    set_state(user_id, WAITING_FOR_PREVIEW)

    office_name = office.get("name") or office.get("office_name") or "Selected office"
    await update.message.reply_text(
        "\n".join(
            [
                "✅ Office Selected",
                "",
                office_name,
                "",
                "Preparing your complaint preview...",
            ]
        )
    )
