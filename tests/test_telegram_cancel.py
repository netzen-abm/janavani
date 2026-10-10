import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

from commands.cancel import cancel
from conversation.session import get_session, set_ephemeral_issue, user_sessions
from conversation.state import get_state, set_state, user_states


def test_cancel_clears_ephemeral_issue_and_workflow_state():
    user_id = 987654
    set_state(user_id, "WAITING_FOR_ISSUE")
    set_ephemeral_issue(user_id, "private citizen narrative")
    assert get_session(user_id)["_ephemeral_issue"] == "private citizen narrative"

    message = SimpleNamespace(reply_text=AsyncMock())
    update = SimpleNamespace(
        effective_user=SimpleNamespace(id=user_id),
        effective_message=message,
    )
    asyncio.run(cancel(update, SimpleNamespace()))

    assert user_id not in user_sessions
    assert user_id not in user_states
    assert get_state(user_id) == "NEW"
    message.reply_text.assert_awaited_once()
    assert "does not delete messages already stored by Telegram" in message.reply_text.await_args.args[0]
