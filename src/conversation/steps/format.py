from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from conversation.session import get_session
from conversation.state import set_state, get_state
from conversation.constants import WAITING_FOR_GENERATE, WAITING_FOR_FORMAT

from conversation.steps.generate import handle_generate


# --------------------------------------------------
# SHOW BUTTONS (SAFE FOR BOTH MESSAGE + CALLBACK)
# --------------------------------------------------

async def show_format_buttons(update: Update):

    keyboard = [
        [
            InlineKeyboardButton("📄 PDF", callback_data="pdf"),
            InlineKeyboardButton("📝 DOCX", callback_data="docx"),
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    # ✅ Handle both message & callback safely
    if update.message:
        await update.message.reply_text(
            "📄 Choose document format:",
            reply_markup=reply_markup
        )
    elif update.callback_query:
        await update.callback_query.message.reply_text(
            "📄 Choose document format:",
            reply_markup=reply_markup
        )


# --------------------------------------------------
# HANDLE BUTTON CLICK
# --------------------------------------------------

async def handle_format(update: Update, context: ContextTypes.DEFAULT_TYPE):

    # --------------------------------------
    # 🔘 CALLBACK FLOW (BUTTON CLICK)
    # --------------------------------------
    if update.callback_query:

        query = update.callback_query
        await query.answer()

        user_id = query.from_user.id

        # 🔒 Check state
        current_state = get_state(user_id)
        if current_state != WAITING_FOR_FORMAT:
            await query.edit_message_text("⚠️ Invalid step. Please restart.")
            return

        session = get_session(user_id)

        # 🎯 Process selection
        if query.data == "pdf":
            session["format"] = "pdf"
        elif query.data == "docx":
            session["format"] = "docx"
        else:
            await query.edit_message_text("❌ Invalid selection.")
            return

        # ✅ Feedback
        await query.edit_message_text(
            f"✅ Format selected: {session['format'].upper()}\n\nGenerating document..."
        )

        # 🔄 Move state
        set_state(user_id, WAITING_FOR_GENERATE)

        # 🚀 Trigger generation
        await handle_generate(update, context)
        return

    # --------------------------------------
    # 📝 TEXT FALLBACK (OPTIONAL BUT STRONG UX)
    # --------------------------------------
    elif update.message:

        user_id = update.effective_user.id
        text = update.message.text.strip().lower()

        if text not in ["pdf", "docx"]:
            await update.message.reply_text(
                "❌ Invalid format.\nType 'pdf' or 'docx'."
            )
            return

        session = get_session(user_id)
        session["format"] = text

        await update.message.reply_text(
            f"✅ Format selected: {text.upper()}\n\nGenerating document..."
        )

        set_state(user_id, WAITING_FOR_GENERATE)

        # 🚀 Trigger generation
        await handle_generate(update, context)