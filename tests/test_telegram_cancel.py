import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

from commands.cancel import cancel
from conversation.session import (
    clear_session,
    get_session,
    purge_expired_ephemeral_issues,
    set_ephemeral_issue,
    user_sessions,
)
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



def test_expired_ephemeral_issue_is_purged_without_another_user_read():
    expired_user, active_user = 987661, 987662
    clear_session(expired_user)
    clear_session(active_user)
    set_ephemeral_issue(expired_user, "expired private narrative")
    set_ephemeral_issue(active_user, "active private narrative")
    get_session(expired_user)["_ephemeral_issue_expires"] = 10.0
    get_session(active_user)["_ephemeral_issue_expires"] = 30.0

    cleared = purge_expired_ephemeral_issues(now=20.0)

    assert cleared == 1
    assert get_session(expired_user)["_ephemeral_issue"] is None
    assert get_session(expired_user)["_ephemeral_issue_expires"] == 0.0
    assert get_session(active_user)["_ephemeral_issue"] == "active private narrative"
    clear_session(expired_user)
    clear_session(active_user)
