from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from conversation.session import get_session
from conversation.state import set_state, get_state
from conversation.constants import WAITING_FOR_GENERATE, WAITING_FOR_FORMAT

from conversation.steps.generate import handle_generate


# --------------------------------------------------
# SHOW BUTTONS (SAFE FOR BOTH MESSAGE + CALLBACK)
# --------------------------------------------------

async def show_format_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = [
        [
            InlineKeyboardButton("📄 PDF", callback_data="pdf"),
            InlineKeyboardButton("📝 DOCX", callback_data="docx"),
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

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
# HANDLE FORMAT SELECTION
# --------------------------------------------------

async def handle_format(update: Update, context: ContextTypes.DEFAULT_TYPE):

    # --------------------------------------
    # 🔘 CALLBACK FLOW (BUTTON CLICK)
    # --------------------------------------
    if update.callback_query:

        query = update.callback_query
        await query.answer()

        user_id = query.from_user.id

        # 🔒 Validate state
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
    # 📝 TEXT INPUT (ENHANCED)
    # --------------------------------------
    elif update.message:

        user_id = update.effective_user.id
        text = update.message.text.strip().lower()

        # 🔒 Validate state
        current_state = get_state(user_id)
        if current_state != WAITING_FOR_FORMAT:
            await update.message.reply_text("⚠️ Invalid step. Please restart.")
            return

        # --------------------------------------
        # ✅ SUPPORT BOTH NUMBER + TEXT
        # --------------------------------------
        if text in ["1", "pdf"]:
            format_selected = "pdf"
        elif text in ["2", "docx"]:
            format_selected = "docx"
        else:
            await update.message.reply_text(
                "❌ Invalid format.\n\nReply:\n1 → PDF\n2 → DOCX"
            )
            return

        session = get_session(user_id)
        session["format"] = format_selected

        await update.message.reply_text(
            f"✅ Format selected: {format_selected.upper()}\n\nGenerating document..."
        )

        set_state(user_id, WAITING_FOR_GENERATE)

        # 🚀 Trigger generation
        await handle_generate(update, context)