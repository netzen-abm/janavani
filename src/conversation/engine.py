"""
Conversation Engine

The engine controls every conversation workflow.

Responsibilities

1. Read current state
2. Execute current step
3. Advance workflow
"""

from conversation.handler import handle_message
from conversation.state import get_state
from conversation.session import get_session


async def run_step(update, context):

    user_id = update.effective_user.id

    state = get_state(user_id)

    session = get_session(user_id)

    print("=" * 60)
    print("ENGINE")
    print("User :", user_id)
    print("State:", state)
    print("Session:", session)
    print("=" * 60)

    await handle_message(update, context)
