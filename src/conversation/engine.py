# src/conversation/engine.py

"""Conversation Engine

Routes the current conversation state to the appropriate workflow step.
Workflow state is routing data, not authorization.
"""

from conversation.state import get_state
from engine.state_registry import get_handler
from authorization.workflow_guard import authorize_workflow_state


async def run_step(update, context):
    """Execute the current workflow step after protected-capability checks."""
    if update.callback_query:
        user_id = update.callback_query.from_user.id
    else:
        user_id = update.effective_user.id

    state = get_state(user_id)

    if state == "NEW":
        if update.message:
            await update.message.reply_text(
                "👋 Welcome to Janavani\n\nUse /complaint to begin."
            )
        return

    handler = get_handler(state)

    if handler is None:
        if update.message:
            await update.message.reply_text(
                "⚠️ Unknown state.\n\nPlease type /start to restart."
            )
        print(f"❌ No handler for state: {state}")
        return

    try:
        # Workflow state is routing data, never authority.
        authorize_workflow_state(user_id, state, interface="telegram")
        await handler(update, context)

    except PermissionError:
        if update.message:
            await update.message.reply_text(
                "⚠️ This action is not authorized.\n\nPlease type /start to restart."
            )

    except Exception as e:
        print("🔥 ERROR OCCURRED")
        print("State:", state)
        print("Error:", str(e))
        import traceback
        traceback.print_exc()
        if update.message:
            await update.message.reply_text(
                "⚠️ Something went wrong.\n\nType /start to restart."
            )
