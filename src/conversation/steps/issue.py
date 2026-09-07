from telegram import Update
from telegram.ext import ContextTypes

from conversation.session import get_session
from conversation.state import set_state
from conversation.constants import WAITING_FOR_DOCUMENT

from services.issue_classifier import classify_issue
from documents.complaint_builder import build_complaint


async def handle_issue(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Capture the issue and bind the conversation to the Telegram principal."""
    user = update.effective_user
    if user is None or update.message is None:
        return

    user_id = user.id
    user_input = update.message.text.strip()
    session = get_session(user_id)
    session["telegram_user_id"] = user_id

    session["issue"] = user_input

    classification = classify_issue(user_input)
    session["category"] = classification["category"]
    session["department"] = classification["department"]

    await update.message.reply_text(
        f"📌 Category: {session['category']}\n"
        f"🏛 Department: {session['department']}"
    )

    # Keep the historical preview for compatibility, but the canonical Case
    # and authority workflow remains authoritative for generation.
    complaint = build_complaint(
        user_name="Anonymous",
        user_address="Not Provided",
        office_id="1",
        issue_text=user_input,
    )
    session["complaint"] = complaint

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
    set_state(user_id, WAITING_FOR_DOCUMENT)
