from telegram import Update
from telegram.ext import ContextTypes

from conversation.session import get_session
from conversation.state import set_state
from conversation.constants import WAITING_FOR_IDENTITY

from documents.complaint_builder import build_complaint


async def handle_preview(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """
    Shows FULL complaint preview before identity selection.
    """

    user_id = update.effective_user.id
    session = get_session(user_id)

    issue = session.get("issue", "")
    office = session.get("office", {})

    # Generate complaint WITHOUT identity
    preview_text = build_complaint(
        issue=issue,
        office=office,
        identity_mode="anonymous"
    )

    await update.message.reply_text(
        f"""
📄 Complaint Preview

{preview_text}

-------------------------

Choose Identity Mode:

1️⃣ Anonymous  
2️⃣ Name Only  
3️⃣ Address Only  
4️⃣ Full Details  

Reply with 1, 2, 3, or 4.
"""
    )

    set_state(
        user_id,
        WAITING_FOR_IDENTITY
    )