"""
Conversation Engine

Routes every conversation state
to the correct workflow step.
"""

from conversation.state import get_state

from conversation.constants import (
    NEW,
)

from conversation.handler import handle_message

from conversation.steps.issue import handle_issue


async def run_step(update, context):

    user_id = update.effective_user.id

    state = get_state(user_id)

    # ----------------------------------
    # New Conversation
    # ----------------------------------

    if state == NEW:

        await handle_issue(update, context)

        return

    # ----------------------------------
    # Remaining workflow
    # (still handled by the old handler)
    # ----------------------------------

    await handle_message(update, context)
