# src/conversation/engine.py

"""
Conversation Engine

Routes the current conversation state
to the appropriate workflow step.
"""

from conversation.state import get_state
from engine.state_registry import get_handler


async def run_step(update, context):
    """
    Execute workflow step
    based on current state
    """

    # 🔐 SAFE USER ID EXTRACTION
    if update.callback_query:
        user_id = update.callback_query.from_user.id
    else:
        user_id = update.effective_user.id

    state = get_state(user_id)

    # --------------------------------------------------
    # 🟢 HANDLE NEW STATE PROPERLY
    # --------------------------------------------------
    if state == "NEW":
        if update.message:
            await update.message.reply_text(
                "👋 Welcome to Janavani\n\n"
                "Use /complaint to begin."
            )
        return

    # --------------------------------------------------
    # 🔵 GET HANDLER
    # --------------------------------------------------
    handler = get_handler(state)

    # --------------------------------------------------
    # 🟡 UNKNOWN STATE
    # --------------------------------------------------
    if handler is None:
        if update.message:
            await update.message.reply_text(
                "⚠️ Something went wrong.\n\n"
                "Please type /start to restart."
            )
        return

    # --------------------------------------------------
    # 🟣 EXECUTE HANDLER
    # --------------------------------------------------
    await handler(update, context)