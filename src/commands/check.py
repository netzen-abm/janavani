from telegram import Update
from telegram.ext import ContextTypes

from services.storage_service import get_complaint_by_id


async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):

    # --------------------------------------------------
    # 🧾 INPUT VALIDATION
    # --------------------------------------------------

    if not context.args:
        await update.message.reply_text(
            "❗ Usage:\n/check <Complaint ID>\n\nExample:\n/check JNV-1234"
        )
        return

    complaint_id = context.args[0]

    # --------------------------------------------------
    # 🔍 FETCH DATA
    # --------------------------------------------------

    record = get_complaint_by_id(complaint_id)

    # --------------------------------------------------
    # ❌ NOT FOUND
    # --------------------------------------------------

    if not record:
        await update.message.reply_text(
            f"❌ No complaint found with ID: {complaint_id}"
        )
        return

    # --------------------------------------------------
    # ✅ FOUND
    # --------------------------------------------------

    response = f"""
📄 Complaint Found

🆔 ID: {record.get("complaint_id")}
📌 Status: {record.get("status")}
🏢 Department: {record.get("department")}
📍 District: {record.get("district")}
"""

    await update.message.reply_text(response.strip())