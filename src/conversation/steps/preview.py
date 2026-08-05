from telegram import Update
from telegram.ext import ContextTypes

from conversation.session import get_session
from conversation.state import set_state
from conversation.constants import WAITING_FOR_IDENTITY


async def handle_preview(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """
    Shows a summary of the complaint
    before asking for identity.
    """

    user_id = update.effective_user.id

    session = get_session(user_id)

    office = session.get("office", {})

    office_name = office.get(
        "office_name",
        "Not Selected"
    )

    await update.message.reply_text(
f"""
📄 Complaint Preview

Issue
------
{session.get("issue", "")}

Document
---------
{session.get("document", "")}

District
---------
{session.get("district", "")}

Office
------
{office_name}

--------------------------------

Choose Identity

1️⃣ Anonymous

2️⃣ Name Only

3️⃣ Full Identity

Reply with:

1

2

or

3
"""
    )

    set_state(
        user_id,
        WAITING_FOR_IDENTITY
    )
