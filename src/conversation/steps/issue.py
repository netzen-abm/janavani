from telegram import Update
from telegram.ext import ContextTypes

from conversation.session import get_session, set_ephemeral_issue
from conversation.state import set_state
from conversation.constants import WAITING_FOR_DOCUMENT

from src.capabilities.issue_classification import classify_issue
from src.adapters.telegram.identity import identity_for_telegram_user


async def handle_issue(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Capture issue transiently; create its Case after authority selection."""
    user = update.effective_user
    if user is None or update.message is None:
        return

    user_id = user.id
    user_input = update.message.text.strip()
    if not user_input:
        await update.message.reply_text("Please describe the civic issue you want to report.")
        return

    links = context.bot_data.get("identity_link_repository")
    try:
        identity_for_telegram_user(user_id, links=links)
    except (PermissionError, LookupError):
        await update.message.reply_text(
            "For your privacy, a Telegram account must be explicitly linked to a "
            "verified Janavani identity before a protected Case can be created. "
            "Account linking is not enabled in this runtime, so no Case was created. "
            "Please do not resend sensitive details until linking is available."
        )
        return

    session = get_session(user_id)
    # Citizen text is held transiently only after identity prerequisites pass.
    set_ephemeral_issue(user_id, user_input)

    classification = classify_issue(user_input)
    session["category"] = classification["category"]
    session["department"] = classification["department"]

    await update.message.reply_text(
        f"📌 Category: {session['category']}\n"
        f"🏛 Department: {session['department']}\n\n"
        "Next, choose the document type, district, and a verified authority. "
        "Janavani will create the Case after the destination is selected."
    )

    set_state(user_id, WAITING_FOR_DOCUMENT)
