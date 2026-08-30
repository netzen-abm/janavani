from telegram import Update
from telegram.ext import ContextTypes

from capabilities.tracking_file import LegacyComplaintTrackingCapability


async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Telegram adapter for the shared Case Tracking capability."""
    if not context.args:
        await update.message.reply_text(
            "❗ Usage:\n/check <Case ID>\n\nExample:\n/check JNV-1234"
        )
        return

    case_id = context.args[0]
    result = LegacyComplaintTrackingCapability().get_status(case_id)

    if not result.ok or result.case is None:
        await update.message.reply_text(
            f"❌ {result.message or 'Case not found.'}"
        )
        return

    case = result.case
    district = case.jurisdiction.get("district")
    department = case.metadata.get("department")

    response = f"""
📄 Case Found

🆔 ID: {case.case_id}
📌 Status: {case.status.value}
🏢 Department: {department or 'Not provided'}
📍 District: {district or 'Not provided'}
"""
    await update.message.reply_text(response.strip())
