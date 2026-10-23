import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

import conversation.session as session_store
from conversation.constants import WAITING_FOR_FORMAT
from conversation.engine import run_step
from conversation.session import clear_session, get_ephemeral_issue, set_ephemeral_issue, user_sessions
from conversation.state import get_state, set_state, user_states


def _seed_expired_workflow(user_id: int, monkeypatch) -> None:
    clear_session(user_id)
    user_states.pop(user_id, None)
    monkeypatch.setattr(session_store, "monotonic", lambda: 0.0)
    set_ephemeral_issue(user_id, "transient citizen narrative")
    set_state(user_id, WAITING_FOR_FORMAT)
    monkeypatch.setattr(session_store, "monotonic", lambda: 901.0)


def test_expired_issue_text_clears_stale_message_workflow(monkeypatch):
    user_id = 882201
    _seed_expired_workflow(user_id, monkeypatch)
    message = SimpleNamespace(reply_text=AsyncMock())
    update = SimpleNamespace(
        callback_query=None,
        effective_user=SimpleNamespace(id=user_id),
        message=message,
        effective_message=message,
    )

    asyncio.run(run_step(update, SimpleNamespace()))

    assert user_id not in user_sessions
    assert user_id not in user_states
    assert get_state(user_id) == "NEW"
    assert get_ephemeral_issue(user_id) is None
    message.reply_text.assert_awaited_once()
    reply = message.reply_text.await_args.args[0]
    assert "expired or was lost after a restart" in reply
    assert "/complaint" in reply
    assert "transient citizen narrative" not in reply


def test_expired_issue_text_clears_stale_inline_callback_workflow(monkeypatch):
    user_id = 882202
    _seed_expired_workflow(user_id, monkeypatch)
    message = SimpleNamespace(reply_text=AsyncMock())
    query = SimpleNamespace(
        from_user=SimpleNamespace(id=user_id),
        answer=AsyncMock(),
    )
    update = SimpleNamespace(
        callback_query=query,
        effective_user=None,
        message=None,
        effective_message=message,
    )

    asyncio.run(run_step(update, SimpleNamespace()))

    query.answer.assert_awaited_once()
    message.reply_text.assert_awaited_once()
    assert user_id not in user_sessions
    assert user_id not in user_states
    assert get_state(user_id) == "NEW"
    assert get_ephemeral_issue(user_id) is None
