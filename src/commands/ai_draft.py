"""Telegram command and callback adapter for the shared civic-draft workflow."""
from __future__ import annotations

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from conversation.constants import (
    COMPLETED,
    WAITING_FOR_CIVIC_DRAFT_CHOICE,
    WAITING_FOR_CIVIC_DRAFT_ISSUE,
    WAITING_FOR_CIVIC_DRAFT_TYPE,
)
from conversation.session import (
    clear_ephemeral_civic_draft,
    get_ephemeral_civic_draft,
    get_session,
    set_ephemeral_civic_draft,
)
from conversation.state import get_state, set_state
from conversation.steps.civic_draft import (
    request_from_transient_draft,
    send_draft_preview,
)
from src.adapters.telegram.identity import identity_for_telegram_user
from src.documents.template_catalogue import get_template, list_templates


def _type_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(item.title, callback_data=f"civicdraft:type:{item.template_id}")]
        for item in list_templates(language="en")
    ])


async def ai_draft_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Start a no-persistence draft flow separate from the canonical Case journey."""
    message = update.effective_message
    user = update.effective_user
    if message is None or user is None:
        return
    if getattr(getattr(message, "chat", None), "type", None) != "private":
        await message.reply_text(
            "For privacy, civic drafting is available only in a private chat with Janavani. "
            "Open the bot directly and use /ai_draft there."
        )
        return
    clear_ephemeral_civic_draft(user.id)
    get_session(user.id).pop("ai_draft_template", None)
    set_state(user.id, WAITING_FOR_CIVIC_DRAFT_TYPE)
    await message.reply_text(
        "Choose a reusable document format. The draft preview is kept only in short-lived "
        "process memory; it is not saved to a Janavani Case or submitted. To support reliable "
        "delivery, pending Telegram updates are encrypted in a processing queue with a 24-hour "
        "expiry window. Expired payloads are cleared when the queue worker is running; if the "
        "worker is unavailable, encrypted payloads may remain until cleanup resumes. Processed "
        "or terminal queue records have their message payload cleared. Telegram also processes "
        "messages sent to this bot. Remote AI improvement is temporarily disabled for free-text "
        "issue narratives and pasted drafts while Janavani implements a privacy-safe minimized-input "
        "boundary. The bot will not send that raw text to a remote AI provider.",
        reply_markup=_type_keyboard(),
    )


async def handle_civic_draft_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Handle template choice, explicit remote-AI request or discard."""
    query = update.callback_query
    if query is None or query.message is None:
        return
    user = query.from_user
    data = str(query.data or "")
    await query.answer()
    if getattr(getattr(query.message, "chat", None), "type", None) != "private":
        await query.message.reply_text(
            "For privacy, civic drafting is available only in a private chat with Janavani. "
            "Restart with /ai_draft in the bot's private chat."
        )
        return
    session = get_session(user.id)
    state = get_state(user.id)

    if data.startswith("civicdraft:type:"):
        if state != WAITING_FOR_CIVIC_DRAFT_TYPE:
            await query.message.reply_text("That menu expired. Use /ai_draft to restart.")
            return
        template_id = data.split(":", 2)[2]
        try:
            template = get_template(template_id)
        except LookupError:
            await query.message.reply_text("That template is unavailable. Use /ai_draft to restart.")
            return
        set_ephemeral_civic_draft(user.id, {
            "template_id": template.template_id,
            "issue": "",
            "subject": "",
            "existing_draft": "",
            "jurisdiction": "",
            "requested_documents": [],
        })
        session["ai_draft_template"] = template.template_id
        set_state(user.id, WAITING_FOR_CIVIC_DRAFT_ISSUE)
        await query.message.reply_text(
            f"Selected: {template.title}\n\nDescribe the issue or purpose in your own words."
        )
        return

    if data == "civicdraft:cancel":
        clear_ephemeral_civic_draft(user.id)
        session.pop("ai_draft_template", None)
        set_state(user.id, COMPLETED)
        await query.message.reply_text("Draft flow discarded. Transient input was cleared.")
        return

    if data != "civicdraft:ai":
        return
    if state != WAITING_FOR_CIVIC_DRAFT_CHOICE:
        await query.message.reply_text("That draft choice expired. Use /ai_draft to restart.")
        return
    current = get_ephemeral_civic_draft(user.id)
    if not current:
        set_state(user.id, COMPLETED)
        await query.message.reply_text("This transient draft expired. Use /ai_draft to restart.")
        return

    # Handle stale/forged callbacks from older keyboards safely. No identity lookup
    # or provider call is performed while remote narrative minimization is unavailable.
    clear_ephemeral_civic_draft(user.id)
    session.pop("ai_draft_template", None)
    set_state(user.id, COMPLETED)
    await query.message.reply_text(
        "Remote AI drafting is temporarily disabled until privacy-safe input minimization "
        "is implemented. No issue narrative or pasted draft was sent to a remote AI provider. "
        "The transient draft was cleared; restart /ai_draft to create a deterministic preview."
    )
