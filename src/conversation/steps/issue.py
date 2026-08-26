from telegram import Update
from telegram.ext import ContextTypes

from conversation.session import get_session
from conversation.state import set_state
from conversation.constants import WAITING_FOR_DOCUMENT
from src.documents.document_contract import StructuredDocument
from src.platform.capability_adapter import dispatch_transport_message
from src.platform.capabilities import build_capability_registry
from src.platform.transport import TransportMessage


async def handle_issue(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Telegram presentation/orchestration layer for complaint intake."""
    user_id = update.effective_user.id
    user_input = update.message.text.strip()
    session = get_session(user_id)

    registry = build_capability_registry()
    message = TransportMessage(
        transport="telegram",
        message_id=str(update.message.message_id),
        conversation_id=str(update.effective_chat.id) if update.effective_chat else None,
        actor_ref=str(user_id),
        text=user_input,
    )
    dispatched = dispatch_transport_message(message, registry, "complaint")
    result = dispatched.result

    if result.status != "completed":
        detail = result.error_code or "UNKNOWN_CAPABILITY_ERROR"
        await update.message.reply_text(f"Unable to prepare the complaint ({detail}).")
        return

    data = result.data or {}
    document = data.get("complaint")
    if not isinstance(document, StructuredDocument):
        await update.message.reply_text("Unable to prepare the complaint (INVALID_DOCUMENT_RESULT).")
        return

    content = dict(document.content)
    session["issue"] = content.get("issue")
    session["category"] = data.get("category")
    session["department"] = data.get("department")
    session["complaint"] = document

    await update.message.reply_text(
        f"📌 Category: {session['category']}\n"
        f"🏛 Department: {session['department']}"
    )

    legal_analysis = document.legal_analysis
    legal_text = "Legal enrichment unavailable." if not legal_analysis else str(legal_analysis)
    preview = f"""
📝 *Complaint Preview*

*Issue:*
{content.get('issue', '')}

*Document ID:*
{document.document_id}

*Legal Analysis:*
{legal_text}

---

Choose next:
1️⃣ Download PDF
2️⃣ Download DOCX
"""

    await update.message.reply_text(preview, parse_mode="Markdown")
    set_state(user_id, WAITING_FOR_DOCUMENT)
