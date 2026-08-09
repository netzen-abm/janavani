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

    # --------------------------------------
    # 🔐 SAFE USER ID EXTRACTION
    # --------------------------------------
    if update.callback_query:
        user_id = update.callback_query.from_user.id
    else:
        user_id = update.effective_user.id

    state = get_state(user_id)

    # --------------------------------------------------
    # 🟢 HANDLE NEW STATE
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
                "⚠️ Unknown state.\n\n"
                "Please type /start to restart."
            )
        print(f"❌ No handler for state: {state}")
        return

    # --------------------------------------------------
    # 🟣 EXECUTE HANDLER (WITH DEBUG)
    # --------------------------------------------------
    try:
        await handler(update, context)

    except Exception as e:
        # 🔥 PRINT FULL ERROR IN TERMINAL
        print("🔥 ERROR OCCURRED")
        print("State:", state)
        print("Error:", str(e))

        # Optional: print full traceback
        import traceback
        traceback.print_exc()

        # 👤 SHOW USER FRIENDLY ERROR
        if update.message:
            await update.message.reply_text(
                f"⚠️ Error: {str(e)}\n\nType /start to restart."
            )