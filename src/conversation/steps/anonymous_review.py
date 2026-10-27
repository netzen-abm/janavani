"""Anonymous draft review and explicit export selection for Telegram."""
from __future__ import annotations

from dataclasses import replace
from io import BytesIO

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, InputFile, Update
from telegram.ext import ContextTypes

from conversation.constants import (
    NEW, WAITING_FOR_ANONYMOUS_REVIEW, WAITING_FOR_ANONYMOUS_FORMAT,
)
from conversation.session import (
    clear_session, get_ephemeral_anonymous_drafts, clear_ephemeral_anonymous_drafts,
    get_session,
)
from conversation.state import get_state, set_state, user_states
from src.documents.anonymous_draft_renderer import render_anonymous_draft


def _review_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("Confirm this draft", callback_data="anon:confirm"),
        InlineKeyboardButton("Cancel", callback_data="anon:cancel"),
    ]])


async def present_anonymous_draft(message, draft, index: int, total: int) -> None:
    """Show text first and make correction semantics explicit."""
    await message.reply_text(
        f"Draft {index + 1} of {total} — {draft.document_type.upper()} (DRAFT ONLY)\n\n"
        f"{draft.title}\n{draft.subject}\n\n{draft.body}\n\n"
        "To correct it, send the complete replacement text for this draft. "
        "Or confirm the displayed version below. Janavani has not created a Case or submitted it.",
        reply_markup=_review_keyboard(),
    )


def _format_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("PDF", callback_data="anon:pdf"),
        InlineKeyboardButton("DOCX", callback_data="anon:docx"),
        InlineKeyboardButton("Both", callback_data="anon:both"),
    ], [InlineKeyboardButton("Cancel", callback_data="anon:cancel")]])


async def handle_anonymous_review(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id if query else (update.effective_user.id if update.effective_user else None)
    if user_id is None:
        return
    state = get_state(user_id)
    stored_drafts = get_ephemeral_anonymous_drafts(user_id)
    drafts = list(stored_drafts) if stored_drafts is not None else None
    if not drafts:
        clear_session(user_id)
        user_states.pop(user_id, None)
        target = query.message if query else update.effective_message
        if query:
            await query.answer()
        if target:
            await target.reply_text("This temporary draft expired. Nothing was saved or submitted. Use /complaint to start again.")
        return

    session = get_session(user_id)
    index = session.get("anonymous_draft_index", 0)
    if not isinstance(index, int) or index < 0 or index >= len(drafts):
        clear_session(user_id)
        user_states.pop(user_id, None)
        if query:
            await query.answer()
        return

    if state == WAITING_FOR_ANONYMOUS_REVIEW:
        if query:
            await query.answer()
            if query.data == "anon:cancel":
                clear_session(user_id)
                user_states[user_id] = NEW
                await query.edit_message_text("Draft cancelled. Temporary draft content was discarded; nothing was submitted.")
                return
            if query.data != "anon:confirm":
                await query.edit_message_text("That action is not valid for this draft. Send a correction or use the current buttons.")
                return
            if index + 1 < len(drafts):
                session["anonymous_draft_index"] = index + 1
                await query.edit_message_text("Draft confirmed for export review. The next draft follows.")
                await present_anonymous_draft(query.message, drafts[index + 1], index + 1, len(drafts))
                return
            set_state(user_id, WAITING_FOR_ANONYMOUS_FORMAT)
            await query.edit_message_text(
                "Draft text confirmed for export. Choose the file format; this does not submit anything.",
                reply_markup=_format_keyboard(),
            )
            return

        message = update.effective_message
        text = (message.text or "").strip() if message else ""
        if not text:
            return
        if text.casefold() in {"/cancel", "cancel"}:
            clear_session(user_id)
            user_states[user_id] = NEW
            await message.reply_text("Draft cancelled. Temporary content was discarded; nothing was submitted.")
            return
        if len(text) > 10000:
            await message.reply_text("The replacement text is too long. Keep it under 10,000 characters.")
            return
        drafts[index] = replace(drafts[index], body=text)
        from conversation.session import set_ephemeral_anonymous_drafts
        set_ephemeral_anonymous_drafts(user_id, drafts)
        await present_anonymous_draft(message, drafts[index], index, len(drafts))
        return

    if state == WAITING_FOR_ANONYMOUS_FORMAT and query:
        await query.answer()
        choice = query.data.removeprefix("anon:")
        if choice == "cancel":
            clear_session(user_id)
            user_states[user_id] = NEW
            await query.edit_message_text("Export cancelled. Temporary content was discarded; nothing was submitted.")
            return
        formats = {"pdf": ("pdf",), "docx": ("docx",), "both": ("pdf", "docx")}
        selected = formats.get(choice)
        if not selected:
            await query.edit_message_text("Invalid format selection. Use the current buttons.")
            return
        failures = []
        for draft in drafts:
            for document_format in selected:
                try:
                    payload, _media_type, extension = render_anonymous_draft(draft, document_format)
                except Exception:
                    failures.append(f"{draft.document_type.upper()} {document_format.upper()}")
                    continue
                await query.message.reply_document(
                    document=InputFile(BytesIO(payload), filename=f"janavani-{draft.document_type}.{extension}"),
                    caption=f"Janavani {draft.document_type.upper()} draft ({extension.upper()}). Draft only; not a registered or submitted Case.",
                )
        await query.message.reply_text(
            ("Some files could not be generated: " + ", ".join(failures) + ". " if failures else "")
            + "Your selected draft export is complete where generation succeeded. Janavani has not created a Case, contacted an authority, or submitted anything."
        )
        clear_session(user_id)
        user_states[user_id] = NEW
