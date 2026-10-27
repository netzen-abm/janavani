import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

from commands.cancel import cancel
from conversation.session import (
    clear_session,
    get_ephemeral_issue,
    get_session,
    purge_expired_ephemeral_issues,
    set_ephemeral_issue,
    user_sessions,
)
from conversation.state import get_state, set_state, user_states


def test_cancel_clears_ephemeral_issue_and_workflow_state():
    user_id = 987654
    clear_session(user_id)
    set_state(user_id, "WAITING_FOR_ISSUE")
    set_ephemeral_issue(user_id, "private citizen narrative")
    assert get_ephemeral_issue(user_id) == "private citizen narrative"
    assert "_ephemeral_issue" not in get_session(user_id)

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
    assert get_ephemeral_issue(user_id) is None
    assert "does not delete messages already stored by Telegram" in message.reply_text.await_args.args[0]



def test_expired_ephemeral_issue_is_purged_without_another_user_read(monkeypatch):
    import conversation.session as session_store

    expired_user, active_user = 987661, 987662
    clear_session(expired_user)
    clear_session(active_user)
    monkeypatch.setattr(session_store, "monotonic", lambda: 0.0)
    set_ephemeral_issue(expired_user, "expired private narrative")
    set_state(expired_user, "WAITING_FOR_FORMAT")
    monkeypatch.setattr(session_store, "monotonic", lambda: 1000.0)
    set_ephemeral_issue(active_user, "active private narrative")

    # Remove unrelated process-local state without changing the test clock.
    session_store._ephemeral_anonymous_drafts.clear()
    session_store._ephemeral_issues.pop(active_user, None)
    cleared = purge_expired_ephemeral_issues(now=1500.0)

    assert cleared == 1
    assert get_ephemeral_issue(expired_user) is None
    assert get_ephemeral_issue(active_user) == "active private narrative"
    assert expired_user not in user_sessions
    assert expired_user not in user_states
    assert "_ephemeral_issue" not in get_session(expired_user)
    assert "_ephemeral_issue" not in get_session(active_user)
    clear_session(expired_user)
    clear_session(active_user)
