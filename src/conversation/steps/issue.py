from telegram import Update
from telegram.ext import ContextTypes

from conversation.session import get_session
from conversation.state import set_state
from conversation.constants import WAITING_FOR_DOCUMENT

from services.issue_classifier import classify_issue
from src.commands.shared_case_capability import create_case_from_telegram
from src.identity.context import IdentityContext
from src.identity.principal import AuthenticationMethod, IdentityMode, Principal


async def handle_issue(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Capture the issue and create the canonical Case through shared infrastructure."""
    user = update.effective_user
    if user is None or update.message is None:
        return

    user_id = user.id
    user_input = update.message.text.strip()
    if not user_input:
        await update.message.reply_text("Please describe the civic issue you want to report.")
        return

    session = get_session(user_id)
    session["telegram_user_id"] = user_id
    session["issue"] = user_input

    classification = classify_issue(user_input)
    session["category"] = classification["category"]
    session["department"] = classification["department"]

    # Channel identifiers are mapped to an opaque principal. The raw Telegram
    # identifier is kept only in the channel session, never as case ownership.
    principal = Principal(
        principal_id=f"tg-session-{user_id}",
        identity_mode=IdentityMode.ANONYMOUS,
        interface="telegram",
        authentication_method=AuthenticationMethod.NONE,
        session_id=str(user_id),
        capabilities=frozenset({"JNV-CIVIC-COMPLAINT"}),
    )
    identity = IdentityContext(principal=principal)
    repository = context.bot_data["case_repository"]
    case = create_case_from_telegram(
        repository,
        identity=identity,
        subject=session["category"],
        narrative=user_input,
    )
    session["case_id"] = case.case_id

    await update.message.reply_text(
        f"📌 Category: {session['category']}\n"
        f"🏛 Department: {session['department']}\n"
        f"🆔 Case: {case.case_id}\n\n"
        "Your issue is now a Janavani case. You can continue to evidence, document, review and consent steps."
    )

    set_state(user_id, WAITING_FOR_DOCUMENT)
