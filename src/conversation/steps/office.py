from telegram import Update
from telegram.ext import ContextTypes

from conversation.session import get_session
from conversation.state import set_state
from conversation.constants import WAITING_FOR_IDENTITY
from capabilities.case_legacy import FileCaseCapability


async def handle_office(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Attach the citizen-selected authority to the shared Case."""
    user_id = update.effective_user.id
    session = get_session(user_id)
    case_id = session.get("case_id")
    offices = session.get("offices", [])

    try:
        choice = int(update.message.text.strip())
    except ValueError:
        await update.message.reply_text("Please enter a valid office number.")
        return

    if choice < 1 or choice > len(offices):
        await update.message.reply_text("Invalid office number.")
        return

    office = offices[choice - 1]
    if not case_id:
        await update.message.reply_text("Your case context is missing. Please type /start to restart.")
        return

    authority = {
        "id": office.get("id") or office.get("authority_id"),
        "name": office.get("office_name") or office.get("name"),
        "type": office.get("type"),
        "jurisdiction": office.get("city") or session.get("district"),
        "source": "directory",
    }

    result = FileCaseCapability().update(case_id, office=authority, district=session.get("district"))
    if not result.ok:
        await update.message.reply_text("We could not save the selected authority to your case. Please try again.")
        return

    session["office"] = authority
    set_state(user_id, WAITING_FOR_IDENTITY)

    await update.message.reply_text(
        f"""✅ Authority Selected

{authority['name']}

Your case is now linked to this authority.

Next, choose how you want to provide your identity information."""
    )
