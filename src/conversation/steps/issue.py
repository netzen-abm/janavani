from telegram import Update
from telegram.ext import ContextTypes

from conversation.session import get_session
from conversation.state import set_state
from conversation.constants import WAITING_FOR_DOCUMENT

from services.issue_classifier import classify_issue
from documents.complaint_builder import build_complaint


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
    # 📝 BUILD COMPLAINT (PREVIEW)
    # --------------------------------------------------

    complaint = build_complaint(
        user_name="Anonymous",
        user_address="Not Provided",
        office_id="1",  # temporary
        issue_text=user_input
    )

    # Save complaint in session (important for next step)
    session["complaint"] = complaint

    # --------------------------------------------------
    # 📄 SHOW PREVIEW
    # --------------------------------------------------

    preview = f"""
📝 *Complaint Preview*

*Issue:*
{complaint['issue']}

*Legal Ground:*
{complaint['law']['law']} - {complaint['law']['section']}

{complaint['law']['explanation']}

---

Choose next:
1️⃣ Download PDF
2️⃣ Download DOCX
"""

    await update.message.reply_text(preview, parse_mode="Markdown")

    # --------------------------------------------------
    # 🔄 NEXT STEP
    # --------------------------------------------------

    set_state(user_id, WAITING_FOR_DOCUMENT)