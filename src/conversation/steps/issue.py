from telegram import Update
from telegram.ext import ContextTypes

from conversation.session import get_session
from conversation.state import set_state
from conversation.constants import WAITING_FOR_DOCUMENT


async def handle_issue(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id

    session = get_session(user_id)

    session["issue"] = update.message.text.strip()

    set_state(
        user_id,
        WAITING_FOR_DOCUMENT
    )

    await update.message.reply_text(
f"""
✅ Your issue has been recorded.

Issue

{session["issue"]}

----------------------------------

Select document

1️⃣ Complaint

2️⃣ RTI

Reply with

1

or

2
"""
    )
