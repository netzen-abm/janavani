"""
Conversation Engine

Executes the current workflow step
using the State Registry.
"""

from conversation.state import get_state
from conversation.handler import handle_message

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

    if handler is not None:

        await handler(update, context)

        return

    # Fallback for legacy states
    await handle_message(update, context)
