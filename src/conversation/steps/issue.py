from telegram import Update
from telegram.ext import ContextTypes

from conversation.session import get_session
from conversation.state import set_state
from conversation.constants import WAITING_FOR_DOCUMENT

from services.issue_classifier import classify_issue
from capabilities.case_legacy import FileCaseCapability


async def handle_issue(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Collect the issue in Telegram and create a shared Janavani Case."""
    user_id = update.effective_user.id
    user_input = update.message.text.strip()
    session = get_session(user_id)

    if not user_input:
        await update.message.reply_text("Please describe the civic issue you want to address.")
        return

    classification = classify_issue(user_input)
    session["issue"] = user_input
    session["category"] = classification.get("category")
    session["department"] = classification.get("department")

    await update.message.reply_text(
        f"📌 Category: {session['category']}\n"
        f"🏛 Department: {session['department']}"
    )

    result = FileCaseCapability().create(
        case_type="complaint",
        issue=user_input,
        metadata={
            "category": session["category"],
            "department": session["department"],
            "channel": "telegram",
            "telegram_user_id": str(user_id),
        },
    )

    if not result.ok or result.case is None:
        await update.message.reply_text(
            "We could not create your case right now. Please try again later."
        )
        return

    session["case_id"] = result.case.case_id
    await update.message.reply_text(
        f"📝 Case created: {result.case.case_id}\n\n"
        "Next, we will identify the appropriate authority before preparing the document."
    )
    set_state(user_id, WAITING_FOR_DOCUMENT)
