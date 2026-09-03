from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from conversation.session import get_session
from conversation.state import set_state, get_state
from conversation.constants import WAITING_FOR_CONSENT, WAITING_FOR_FORMAT


async def show_format_buttons(update: Update):
    keyboard = [[
        InlineKeyboardButton("📄 PDF", callback_data="pdf"),
        InlineKeyboardButton("📝 DOCX", callback_data="docx"),
    ]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.message:
        await update.message.reply_text(
            "📄 Choose document format:",
            reply_markup=reply_markup,
        )
    elif update.callback_query:
        await update.callback_query.message.reply_text(
            "📄 Choose document format:",
            reply_markup=reply_markup,
        )


async def _request_consent(update: Update):
    message = update.callback_query.message if update.callback_query else update.message
    await message.reply_text(
        "Before generating the document, please confirm:\n\n"
        "I consent to JanaVani recording this case and preparing the selected "
        "document for my review/printing. This does not mean the government "
        "has received or acknowledged it.\n\n"
        "Reply YES to continue or NO to cancel."
    )


async def handle_format(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        user_id = query.from_user.id

        if get_state(user_id) != WAITING_FOR_FORMAT:
            await query.edit_message_text("⚠️ Invalid step. Please restart.")
            return

        session = get_session(user_id)
        if query.data not in {"pdf", "docx"}:
            await query.edit_message_text("❌ Invalid selection.")
            return

        session["format"] = query.data
        await query.edit_message_text(
            f"✅ Format selected: {query.data.upper()}"
        )
        set_state(user_id, WAITING_FOR_CONSENT)
        await _request_consent(update)
        return

    if update.message:
        user_id = update.effective_user.id
        text = update.message.text.strip().lower()

        if text not in {"pdf", "docx"}:
            await update.message.reply_text(
                "❌ Invalid format.\nType 'pdf' or 'docx'."
            )
            return

        session = get_session(user_id)
        session["format"] = text
        set_state(user_id, WAITING_FOR_CONSENT)
        await _request_consent(update)
