import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

import conversation.session as session_store
from conversation.constants import WAITING_FOR_DOCUMENT, WAITING_FOR_FORMAT
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
        effective_chat=SimpleNamespace(type="private"),
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
        effective_chat=SimpleNamespace(type="private"),
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



def test_inline_callback_after_process_restart_is_acknowledged(monkeypatch):
    user_id = 882203
    clear_session(user_id)
    user_states.pop(user_id, None)
    message = SimpleNamespace(reply_text=AsyncMock())
    query = SimpleNamespace(
        from_user=SimpleNamespace(id=user_id),
        answer=AsyncMock(),
    )
    update = SimpleNamespace(
        callback_query=query,
        effective_chat=SimpleNamespace(type="private"),
        effective_user=None,
        message=None,
        effective_message=message,
    )

    asyncio.run(run_step(update, SimpleNamespace()))

    query.answer.assert_awaited_once()
    message.reply_text.assert_awaited_once()
    assert "earlier workflow" in message.reply_text.await_args.args[0]
    assert "/complaint" in message.reply_text.await_args.args[0]



def test_new_conversation_processes_first_plain_text_as_issue(monkeypatch):
    import conversation.steps.issue as issue_step

    user_id = 882204
    clear_session(user_id)
    user_states.pop(user_id, None)
    monkeypatch.setattr(
        issue_step,
        "identity_for_telegram_user",
        lambda user_id, links: object(),
    )
    monkeypatch.setattr(
        issue_step,
        "classify_issue",
        lambda _text: SimpleNamespace(
            category="Streetlight outage",
            department="Municipality",
        ),
    )
    replies = []

    async def reply_text(text):
        replies.append(text)

    message = SimpleNamespace(
        text="The streetlight has been broken for three nights",
        reply_text=reply_text,
    )
    update = SimpleNamespace(
        callback_query=None,
        effective_chat=SimpleNamespace(type="private"),
        effective_user=SimpleNamespace(id=user_id),
        message=message,
        effective_message=message,
    )

    asyncio.run(run_step(update, SimpleNamespace(bot_data={})))

    assert get_state(user_id) == WAITING_FOR_DOCUMENT
    assert get_ephemeral_issue(user_id) == message.text
    assert replies and "Streetlight outage" in replies[0]
    clear_session(user_id)
    user_states.pop(user_id, None)


def test_group_message_is_rejected_before_issue_text_is_retained():
    user_id = 882205
    clear_session(user_id)
    user_states.pop(user_id, None)
    set_state(user_id, "WAITING_FOR_ISSUE")
    message = SimpleNamespace(
        text="My private address and civic complaint",
        reply_text=AsyncMock(),
    )
    update = SimpleNamespace(
        callback_query=None,
        effective_chat=SimpleNamespace(type="group"),
        effective_user=SimpleNamespace(id=user_id),
        message=message,
        effective_message=message,
    )

    asyncio.run(run_step(update, SimpleNamespace()))

    assert get_ephemeral_issue(user_id) is None
    assert user_id not in user_sessions
    assert get_state(user_id) == "WAITING_FOR_ISSUE"
    message.reply_text.assert_awaited_once()
    assert "private chat" in message.reply_text.await_args.args[0]
    clear_session(user_id)
    user_states.pop(user_id, None)


def test_complaint_command_in_group_does_not_reset_or_start_workflow():
    from commands.complaint import complaint

    user_id = 882206
    clear_session(user_id)
    user_states.pop(user_id, None)
    set_state(user_id, WAITING_FOR_FORMAT)
    set_ephemeral_issue(user_id, "existing private narrative")
    message = SimpleNamespace(reply_text=AsyncMock())
    update = SimpleNamespace(
        effective_chat=SimpleNamespace(type="group"),
        effective_user=SimpleNamespace(id=user_id),
        message=message,
    )

    asyncio.run(complaint(update, SimpleNamespace()))

    assert get_state(user_id) == WAITING_FOR_FORMAT
    assert get_ephemeral_issue(user_id) == "existing private narrative"
    message.reply_text.assert_awaited_once()
    assert "private chat" in message.reply_text.await_args.args[0]
    clear_session(user_id)
    user_states.pop(user_id, None)


def test_explicit_translation_request_is_not_treated_as_a_new_complaint():
    user_id = 882207
    clear_session(user_id)
    user_states.pop(user_id, None)
    message = SimpleNamespace(
        text="Can you translate it in Malayalam",
        reply_text=AsyncMock(),
    )
    update = SimpleNamespace(
        callback_query=None,
        effective_chat=SimpleNamespace(type="private"),
        effective_user=SimpleNamespace(id=user_id),
        message=message,
        effective_message=message,
    )

    asyncio.run(run_step(update, SimpleNamespace(bot_data={})))

    message.reply_text.assert_awaited_once()
    reply = message.reply_text.await_args.args[0]
    assert "translation" in reply.lower()
    assert "Malayalam" in reply
    assert "not enabled yet" in reply
    assert get_ephemeral_issue(user_id) is None
    assert user_id not in user_sessions
    assert user_id not in user_states
