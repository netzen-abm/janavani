from telegram import Update
from telegram.ext import ContextTypes

from conversation.session import get_session
from conversation.state import set_state

from conversation.constants import WAITING_FOR_FORMAT


async def handle_preview(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    user_id = update.effective_user.id
    session = get_session(user_id)

    # --------------------------------------
    # 🧹 SAFE EXTRACTION
    # --------------------------------------

    issue = session.get("issue", "Not provided")
    category = session.get("category", "Not classified")
    department = session.get("department", "Unknown")
    district = session.get("district", "Unknown")

    office = session.get("office", {})
    office_name = office.get("name", "Not specified")
    office_city = office.get("city", "")

    name = session.get("citizen_name", "Anonymous")
    address = session.get("address", "Not provided")

    # --------------------------------------
    # 📄 BUILD PREVIEW
    # --------------------------------------

    preview_text = f"""
📄 Complaint Preview

📝 Issue:
{issue}

📌 Category: {category}
🏛 Department: {department}
📍 District: {district}

🏢 Office:
{office_name} {f"({office_city})" if office_city else ""}

👤 Name: {name}
🏠 Address: {address}

-----------------------------------

Generate document?

Reply:
1 → PDF
2 → DOCX
"""

    await update.message.reply_text(preview_text)

    # --------------------------------------
    # ➡️ NEXT STEP
    # --------------------------------------

    set_state(user_id, WAITING_FOR_FORMAT)