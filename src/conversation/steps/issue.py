from io import BytesIO

from telegram import InputFile, Update
from telegram.ext import ContextTypes

from conversation.session import clear_session, get_session, set_ephemeral_issue
from conversation.state import set_state, user_states
from conversation.constants import NEW, WAITING_FOR_DOCUMENT
from src.capabilities.issue_classification import classify_issue
from src.adapters.telegram.identity import identity_for_telegram_user
from src.capabilities.anonymous_civic_drafting import (
    build_anonymous_drafts,
    recommend_document_types,
)
from src.documents.anonymous_draft_renderer import render_anonymous_draft


async def _send_anonymous_drafts(update: Update, user_id: int, narrative: str) -> None:
    """Generate citizen-owned drafts without identity, Case creation, or persistence."""
    message = update.message
    if message is None:
        return
    try:
        drafts = build_anonymous_drafts(narrative)
        _types, explanation = recommend_document_types(narrative)
        await message.reply_text(
            "🔎 Janavani's suggestion\n\n"
            + explanation
            + "\n\nI'll prepare the suggested draft(s) now. No account is needed."
        )
        for draft in drafts:
            await message.reply_text(
                f"📄 Preparing {draft.document_type.upper()} draft. "
                "Review the facts and fill every placeholder before sending."
            )
            for document_format in ("pdf", "docx"):
                try:
                    payload, _media_type, extension = render_anonymous_draft(
                        draft, document_format
                    )
                except Exception as exc:
                    # A renderer outage must not leak user content or suppress another format.
                    await message.reply_text(
                        f"The {extension if 'extension' in locals() else document_format.upper()} "
                        "file could not be generated. You can still review the draft in the next message."
                    )
                    continue
                await message.reply_document(
                    document=InputFile(
                        BytesIO(payload),
                        filename=f"janavani-{draft.document_type}.{extension}",
                    ),
                    caption=(
                        f"Janavani {draft.document_type.upper()} draft ({extension.upper()}). "
                        "This is an editable citizen draft, not a registered or submitted case."
                    ),
                )
            await message.reply_text(draft.body)
        await message.reply_text(
            "✅ Your draft(s) are ready. Janavani has not registered a Case, contacted an "
            "authority, or submitted anything. Keep your own copy.\n\n"
            "To track a case or continue across devices, account sign-in/pairing is optional "
            "where configured. Use /privacy to review data handling. Do not resend sensitive "
            "details unless they are necessary."
        )
    except ValueError as exc:
        await message.reply_text(
            "Please provide a little more detail in a complete sentence. "
            "No case was created."
        )
    finally:
        clear_session(user_id)
        user_states[user_id] = NEW


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
