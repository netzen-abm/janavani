"""
Conversation Engine

Routes every conversation state
to the correct workflow step.
"""

from conversation.state import get_state

from conversation.constants import (
    NEW,
    WAITING_FOR_DOCUMENT,
    WAITING_FOR_DISTRICT,
)

from conversation.handler import handle_message

from conversation.steps.issue import handle_issue
from conversation.steps.document import handle_document
from conversation.steps.district import handle_district


async def run_step(update, context):

    user_id = update.effective_user.id

    state = get_state(user_id)

    # New conversation
    if state == NEW:

        await handle_issue(update, context)
        return

    # Document selection
    if state == WAITING_FOR_DOCUMENT:

        await handle_document(update, context)
        return

    # District selection
    if state == WAITING_FOR_DISTRICT:

        await handle_district(update, context)
        return

    # Remaining workflow
    await handle_message(update, context)
