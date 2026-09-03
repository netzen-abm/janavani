from telegram import Update
from telegram.ext import ContextTypes

from conversation.session import get_session
from conversation.state import set_state

from conversation.constants import (
    WAITING_FOR_OFFICE_FALLBACK,
    WAITING_FOR_OFFICE_MANUAL,
)

from services.authority_service import find_authorities


async def handle_select_office(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    user_id = update.effective_user.id
    location = update.message.text.strip()

    session = get_session(user_id)
    department = session.get("department", "")

    authorities = find_authorities(department, location)

    if not authorities:
        await update.message.reply_text(
            "⚠️ No exact office found.\n\n"
            "You can still continue:\n\n"
            "1 → Enter office manually\n"
            "2 → Continue without office\n\n"
            "Reply with 1 or 2."
        )
        session["office"] = None
        set_state(user_id, WAITING_FOR_OFFICE_FALLBACK)
        return

    session["authorities"] = authorities
    session["offices"] = [
        {
            "id": authority.authority_id,
            "name": authority.name,
            "type": authority.authority_type,
            "city": authority.jurisdiction.get("city", ""),
            "address": (
                authority.primary_contact.address
                if authority.primary_contact
                else ""
            ),
            "officer_role": (
                authority.primary_contact.role
                if authority.primary_contact
                else ""
            ),
            "email": (
                authority.primary_contact.email
                if authority.primary_contact
                else None
            ),
        }
        for authority in authorities
    ]

    msg = "🏢 Found offices:\n\n"
    for index, authority in enumerate(authorities, start=1):
        city = authority.jurisdiction.get("city", "")
        msg += f"{index}. {authority.name} ({city})\n"

    msg += "\nReply with office number."
    await update.message.reply_text(msg)

    # TEMP: route to manual handler until selection step is built.
    set_state(user_id, WAITING_FOR_OFFICE_MANUAL)
