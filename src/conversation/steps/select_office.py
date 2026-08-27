from telegram import Update
from telegram.ext import ContextTypes

from conversation.session import get_session
from conversation.state import set_state

from conversation.constants import (
    WAITING_FOR_OFFICE,
    WAITING_FOR_OFFICE_FALLBACK,
)

from services.authority_service import find_authorities


def _authority_to_session_record(authority) -> dict:
    """Keep the Telegram session transport-shaped while using the canonical Authority."""
    return {
        "id": authority.authority_id,
        "name": authority.name,
        "city": authority.jurisdiction.get("city", ""),
        "address": authority.postal_addresses[0] if authority.postal_addresses else "",
        "phone": authority.contact_points[0] if authority.contact_points else "",
        "website": authority.official_urls[0] if authority.official_urls else "",
        "authority_id": authority.authority_id,
        "verification_status": authority.verification_status.value,
        "source_refs": [source.source_id for source in authority.source_refs],
    }


async def handle_select_office(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    user_id = update.effective_user.id
    location = update.message.text.strip()

    session = get_session(user_id)
    department = session.get("department", "")

    try:
        authorities = find_authorities(department, location)
    except ValueError:
        await update.message.reply_text(
            "⚠️ I need a department and location before I can find the appropriate authority."
        )
        set_state(user_id, WAITING_FOR_OFFICE_FALLBACK)
        return

    if not authorities:
        await update.message.reply_text(
            "⚠️ No exact authority found.\n\n"
            "You can still continue:\n\n"
            "1 → Enter office manually\n"
            "2 → Continue without office\n\n"
            "Reply with 1 or 2."
        )
        session["office"] = None
        set_state(user_id, WAITING_FOR_OFFICE_FALLBACK)
        return

    offices = [_authority_to_session_record(authority) for authority in authorities]
    session["offices"] = offices

    msg = "🏢 Found authorities:\n\n"
    for i, office in enumerate(offices, start=1):
        msg += f"{i}. {office['name']} ({office.get('city', '')})\n"

    msg += "\nReply with office number."
    await update.message.reply_text(msg)
    set_state(user_id, WAITING_FOR_OFFICE)
