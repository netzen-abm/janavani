from telegram import Update
from telegram.ext import ContextTypes

from conversation.session import get_session
from conversation.state import set_state
from conversation.constants import WAITING_FOR_OFFICE_FALLBACK, WAITING_FOR_OFFICE
from capabilities.authority_directory import DirectoryAuthorityCapability


async def handle_select_office(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Discover authorities through the shared Authority capability."""
    user_id = update.effective_user.id
    location = update.message.text.strip()
    session = get_session(user_id)
    department = session.get("department", "")

    candidates = DirectoryAuthorityCapability().discover(
        query=department,
        jurisdiction=location,
    )

    if not candidates:
        await update.message.reply_text(
            "⚠️ No exact authority found.\n\n"
            "1 → Enter authority manually\n"
            "2 → Continue without authority\n\n"
            "Reply with 1 or 2."
        )
        session["offices"] = []
        set_state(user_id, WAITING_FOR_OFFICE_FALLBACK)
        return

    session["offices"] = [
        {
            "id": candidate.authority_id,
            "name": candidate.name,
            "office_name": candidate.name,
            "type": candidate.authority_type,
            "city": candidate.jurisdiction,
        }
        for candidate in candidates
    ]

    msg = "🏢 Found authorities:\n\n"
    for i, candidate in enumerate(candidates, start=1):
        msg += f"{i}. {candidate.name} ({candidate.jurisdiction or ''})\n"
    msg += "\nReply with authority number."

    await update.message.reply_text(msg)
    set_state(user_id, WAITING_FOR_OFFICE)
