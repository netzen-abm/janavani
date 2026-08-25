from telegram import Update
from telegram.ext import ContextTypes

from conversation.session import get_session
from conversation.state import set_state
from conversation.constants import WAITING_FOR_DOCUMENT
from platform.capability_adapter import dispatch_transport_message
from platform.registry import CapabilityRegistry
from platform.transport import TransportMessage
from capabilities.complaint import ComplaintCapability


async def handle_issue(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Telegram presentation/orchestration layer for complaint intake."""
    user_id = update.effective_user.id
    user_input = update.message.text.strip()
    session = get_session(user_id)

    registry = CapabilityRegistry()
    registry.register(ComplaintCapability())
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
        await update.message.reply_text(result.message or "Unable to prepare the complaint.")
        return

    data = result.data or {}
    session["issue"] = data.get("issue")
    session["category"] = data.get("category")
    session["department"] = data.get("department")
    session["complaint"] = data.get("complaint")

    await update.message.reply_text(
        f"📌 Category: {session['category']}\n"
        f"🏛 Department: {session['department']}"
    )

    complaint = session["complaint"]
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
