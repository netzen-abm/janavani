from telegram import Update
from telegram.ext import ContextTypes

from services.storage_service import get_complaint_by_id
from src.authorization.capabilities import PUBLIC_CAPABILITIES
from src.authorization.guards import require_capability
from src.authorization.policy import AuthorizationPolicy
from src.identity.context import anonymous_context


async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Telegram adapter for possession-based public complaint status lookup."""
    if not context.args:
        await update.message.reply_text(
            "❗ Usage:\n/check <Complaint ID>\n\nExample:\n/check JNV-1234"
        )
        return

    identity = anonymous_context(
        f"telegram-session:{update.effective_chat.id}",
        interface="telegram",
    )
    require_capability(
        identity,
        "public.complaint_status",
        policy=AuthorizationPolicy(anonymous_capabilities=PUBLIC_CAPABILITIES),
    )

    complaint_id = context.args[0]
    record = get_complaint_by_id(complaint_id)

    if not record:
        await update.message.reply_text(
            f"❌ No complaint found with ID: {complaint_id}"
        )
        return

    response = f"""
📄 Complaint Found

🆔 ID: {record.get("complaint_id")}
📌 Status: {record.get("status")}
🏢 Department: {record.get("department")}
📍 District: {record.get("district")}
"""
    await update.message.reply_text(response.strip())
