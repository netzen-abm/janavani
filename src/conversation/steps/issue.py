from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from conversation.session import (clear_session, get_session, set_ephemeral_issue, set_ephemeral_anonymous_drafts)
from conversation.state import set_state, user_states
from conversation.steps.anonymous_review import present_anonymous_draft
from conversation.constants import NEW, WAITING_FOR_DOCUMENT, WAITING_FOR_ANONYMOUS_REVIEW
from src.capabilities.issue_classification import classify_issue
from src.adapters.telegram.identity import identity_for_telegram_user
from src.capabilities.anonymous_civic_drafting import (
    build_anonymous_drafts,
    recommend_document_types,
)



async def present_anonymous_draft(message, draft, index: int, total: int) -> None:
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Confirm this draft", callback_data="anon:confirm"),
         InlineKeyboardButton("Cancel", callback_data="anon:cancel")],
    ])
    await message.reply_text(
        f"Draft {index + 1} of {total} — {draft.document_type.upper()} (DRAFT ONLY)\n\n"
        f"{draft.title}\n{draft.subject}\n\n{draft.body}\n\n"
        "Reply with the complete corrected text to replace this draft, or confirm it below. "
        "Do not include unnecessary sensitive information.",
        reply_markup=keyboard,
    )


async def _send_anonymous_drafts(update: Update, user_id: int, narrative: str) -> None:
    """Start anonymous text review without rendering files or creating a Case."""
    message = update.message
    if message is None:
        return
    try:
        drafts = build_anonymous_drafts(narrative)
        _types, explanation = recommend_document_types(narrative)
        set_ephemeral_anonymous_drafts(user_id, drafts)
        session = get_session(user_id)
        session["anonymous_draft_index"] = 0
        await message.reply_text(
            "🔎 Janavani's suggestion\n\n" + explanation
            + "\n\nI'll show the draft text first. Review and correct it before choosing PDF or DOCX. "
            "No account is needed, and this does not create or submit a Case."
        )
        set_state(user_id, WAITING_FOR_ANONYMOUS_REVIEW)
        await present_anonymous_draft(message, drafts[0], 0, len(drafts))
    except ValueError:
        clear_session(user_id)
        user_states[user_id] = NEW
        await message.reply_text("Please provide a little more detail in a complete sentence. No case was created.")


async def handle_issue(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Capture the initial narrative; anonymous users receive drafts immediately."""
    user = update.effective_user
    if user is None or update.message is None:
        return

    user_id = user.id
    user_input = (update.message.text or "").strip()
    words = user_input.split()
    if len(user_input) > 5000:
        await update.message.reply_text(
            "Your description is too long. Please keep it under 5,000 characters."
        )
        return
    if len(words) < 2 or not any(any(ch.isalpha() for ch in word) for word in words):
        await update.message.reply_text(
            "Please describe the issue in a short sentence, for example: "
            "'My road has been damaged for three months.'"
        )
        return

    # The dispatcher uses this short-lived buffer as the workflow expiry guard.
    set_ephemeral_issue(user_id, user_input)
    links = context.bot_data.get("identity_link_repository")
    try:
        identity_for_telegram_user(user_id, links=links)
    except (PermissionError, LookupError):
        # No login is required to create a draft. A tracked Case still uses the
        # verified identity/capability path below; these drafts remain transient.
        await _send_anonymous_drafts(update, user_id, user_input)
        return

    session = get_session(user_id)
    set_ephemeral_issue(user_id, user_input)
    classification = classify_issue(user_input)
    session["category"] = classification.category
    session["department"] = classification.department

    await update.message.reply_text(
        f"📌 Category: {session['category']}\n"
        f"🏛 Department: {session['department']}\n\n"
        "Next, choose the document type, district, and a verified authority. "
        "Janavani will create the Case after the destination is selected."
    )
    set_state(user_id, WAITING_FOR_DOCUMENT)
