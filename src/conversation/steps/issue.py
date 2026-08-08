from telegram import Update
from telegram.ext import ContextTypes

from conversation.session import get_session
from conversation.state import set_state
from conversation.constants import WAITING_FOR_DOCUMENT

from services.issue_classifier import classify_issue


async def handle_issue(update: Update, context: ContextTypes.DEFAULT_TYPE):

    # --------------------------------------------------
    # 🔐 USER + INPUT
    # --------------------------------------------------

    user_id = update.effective_user.id
    user_input = update.message.text.strip()

    session = get_session(user_id)

    # --------------------------------------------------
    # 📝 SAVE ISSUE
    # --------------------------------------------------

    session["issue"] = user_input

    # --------------------------------------------------
    # 🧠 CLASSIFY ISSUE
    # --------------------------------------------------

    classification = classify_issue(user_input)

    session["category"] = classification["category"]
    session["department"] = classification["department"]

    # --------------------------------------------------
    # 📤 FEEDBACK TO USER
    # --------------------------------------------------

    await update.message.reply_text(
        f"📌 Category: {session['category']}\n"
        f"🏛 Department: {session['department']}"
    )

    # --------------------------------------------------
    # 🔄 NEXT STEP
    # --------------------------------------------------

    set_state(user_id, WAITING_FOR_DOCUMENT)

    await update.message.reply_text(
        "📄 Select document type (coming next step)"
    )