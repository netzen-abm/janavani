"""Telegram text-state handlers and preview presentation for civic drafting."""
from __future__ import annotations

from io import BytesIO

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, InputFile, Update
from telegram.ext import ContextTypes

from conversation.constants import (
    COMPLETED,
    WAITING_FOR_CIVIC_DRAFT_CHOICE,
    WAITING_FOR_CIVIC_DRAFT_EXISTING,
    WAITING_FOR_CIVIC_DRAFT_ISSUE,
    WAITING_FOR_CIVIC_DRAFT_JURISDICTION,
    WAITING_FOR_CIVIC_DRAFT_RECORDS,
    WAITING_FOR_CIVIC_DRAFT_TYPE,
)
from conversation.session import (
    get_ephemeral_civic_draft,
    set_ephemeral_civic_draft,
)
from conversation.state import get_state, set_state
from src.services.civic_draft_workflow import CivicDraftPreviewRequest, CivicDraftPreviewWorkflow

_MAX_ISSUE = 5_000
_MAX_DRAFT = 8_000

def request_from_transient_draft(data: dict) -> CivicDraftPreviewRequest:
    return CivicDraftPreviewRequest(
        template_id=data["template_id"],
        issue=data["issue"],
        subject=data.get("subject", ""),
        existing_draft=data.get("existing_draft", ""),
        jurisdiction=data.get("jurisdiction", ""),
        requested_documents=tuple(data.get("requested_documents", [])),
    )


def _result_keyboard() -> InlineKeyboardMarkup:
    # Remote AI is intentionally not offered until input minimization is tested.
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("Discard", callback_data="civicdraft:cancel"),
    ]])

async def handle_civic_draft_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Advance only this user's TTL-bounded template-preview flow."""
    message = update.effective_message
    user = update.effective_user
    if message is None or user is None or not message.text:
        return
    state = get_state(user.id)
    text = message.text.strip()
    if state == WAITING_FOR_CIVIC_DRAFT_TYPE:
        await message.reply_text("Choose a document format using the buttons above.")
        return
    if state == WAITING_FOR_CIVIC_DRAFT_CHOICE:
        await message.reply_text("Use the Discard button on the draft file to clear the transient input.")
        return
    current = get_ephemeral_civic_draft(user.id)
    if not current:
        set_state(user.id, COMPLETED)
        await message.reply_text("This transient draft expired. Use /ai_draft to restart.")
        return

    if state == WAITING_FOR_CIVIC_DRAFT_ISSUE:
        if not text or len(text) > _MAX_ISSUE:
            await message.reply_text("Describe the issue in 1 to 5,000 characters.")
            return
        current["issue"] = text
        if current["template_id"] in {"rti.records", "administrative.evidence-demand"}:
            set_state(user.id, WAITING_FOR_CIVIC_DRAFT_JURISDICTION)
            await message.reply_text("Which public authority or jurisdiction is this document for?")
        else:
            set_state(user.id, WAITING_FOR_CIVIC_DRAFT_EXISTING)
            await message.reply_text(
                "Paste an existing draft to improve, or send a single dash (-) to skip this step."
            )
        set_ephemeral_civic_draft(user.id, current)
        return

    if state == WAITING_FOR_CIVIC_DRAFT_JURISDICTION:
        if not text or len(text) > 300:
            await message.reply_text("Enter the public authority or jurisdiction (up to 300 characters).")
            return
        current["jurisdiction"] = text
        set_ephemeral_civic_draft(user.id, current)
        if current["template_id"] == "rti.records":
            set_state(user.id, WAITING_FOR_CIVIC_DRAFT_RECORDS)
            await message.reply_text(
                "List the existing records you are requesting, one per line. "
                "RTI drafts request records; they do not ask the authority to create a new explanation."
            )
        else:
            set_state(user.id, WAITING_FOR_CIVIC_DRAFT_EXISTING)
            await message.reply_text(
                "Paste the notice or your existing reply to improve, or send a single dash (-) to use the reusable starter format."
            )
        return

    if state == WAITING_FOR_CIVIC_DRAFT_RECORDS:
        records = [line.strip() for line in text.splitlines() if line.strip()]
        if not records or len(records) > 12 or any(len(item) > 800 for item in records):
            await message.reply_text("Enter 1 to 12 existing records, each no longer than 800 characters.")
            return
        current["requested_documents"] = records
        set_ephemeral_civic_draft(user.id, current)
        set_state(user.id, WAITING_FOR_CIVIC_DRAFT_EXISTING)
        await message.reply_text(
            "Paste an existing RTI draft to improve, or send a single dash (-) to skip this step."
        )
        return

    if state == WAITING_FOR_CIVIC_DRAFT_EXISTING:
        if text != "-" and len(text) > _MAX_DRAFT:
            await message.reply_text("The existing draft must be 8,000 characters or fewer.")
            return
        current["existing_draft"] = "" if text == "-" else text
        set_ephemeral_civic_draft(user.id, current)
        try:
            preview = CivicDraftPreviewWorkflow().preview(request_from_transient_draft(current))
        except (LookupError, ValueError):
            await message.reply_text("The selected template needs more details. Use /ai_draft to restart.")
            return
        await send_draft_preview(message, preview, remote_requested=False)
        set_state(user.id, WAITING_FOR_CIVIC_DRAFT_CHOICE)
        return

    await message.reply_text("Use /ai_draft to begin or continue the civic-draft preview.")


async def send_draft_preview(message, result: dict, *, remote_requested: bool) -> None:
    """Send a bounded text artifact as an ephemeral preview, never as submission."""
    body = str(result["draft_body"])
    if len(body) > 20_000:
        body = body[:20_000] + "\n\n[Preview truncated to the safety limit.]"
    content = BytesIO(body.encode("utf-8"))
    content.seek(0)
    caption = (
        f"Template: {result['template_id']} v{result['template_version']} · "
        f"AI used: {'Yes' if result['ai_used'] else 'No'} · status: {result['ai_status']}. "
        "Not saved or submitted. Review facts and legal references before use."
    )
    await message.reply_document(
        document=InputFile(content, filename="janavani-civic-draft.txt"),
        caption=caption[:1000],
        reply_markup=_result_keyboard() if not remote_requested else None,
    )
