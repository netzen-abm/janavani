"""
Conversation Engine

Routes the current conversation state
to the appropriate workflow step.

This is the single entry point for the
new conversation architecture.
"""

from conversation.state import get_state

from engine.state_registry import get_handler


async def run_step(update, context):
    """
    Execute the workflow step
    associated with the user's
    current conversation state.
    """

    user_id = update.effective_user.id

    state = get_state(user_id)

    handler = get_handler(state)

    if handler is None:

        await update.message.reply_text(
            """
⚠️ Unknown conversation state.

Please type /start to begin a new conversation.
"""
        )

        return

    await handler(update, context)
