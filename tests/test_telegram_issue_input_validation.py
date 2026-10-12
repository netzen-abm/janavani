import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest

from conversation.steps import issue


@pytest.mark.parametrize("text", ["", "   ", "hjhdgj", "x" * 5001])
def test_issue_rejects_empty_noise_or_oversized_input_before_identity_lookup(
    monkeypatch, text
):
    identity_lookup = Mock(side_effect=AssertionError("must not resolve identity"))
    save_ephemeral = Mock(side_effect=AssertionError("must not retain rejected text"))
    advance_state = Mock(side_effect=AssertionError("must not advance rejected input"))
    monkeypatch.setattr(issue, "identity_for_telegram_user", identity_lookup)
    monkeypatch.setattr(issue, "set_ephemeral_issue", save_ephemeral)
    monkeypatch.setattr(issue, "set_state", advance_state)

    message = SimpleNamespace(text=text, reply_text=AsyncMock())
    update = SimpleNamespace(
        effective_user=SimpleNamespace(id=7001),
        message=message,
    )
    context = SimpleNamespace(bot_data={})

    asyncio.run(issue.handle_issue(update, context))

    identity_lookup.assert_not_called()
    save_ephemeral.assert_not_called()
    advance_state.assert_not_called()
    message.reply_text.assert_awaited_once()


def test_issue_description_gate_accepts_a_short_sentence_for_next_step(monkeypatch):
    identity_lookup = Mock(side_effect=PermissionError("not linked"))
    monkeypatch.setattr(issue, "identity_for_telegram_user", identity_lookup)

    message = SimpleNamespace(
        text="My road is damaged",
        reply_text=AsyncMock(),
    )
    update = SimpleNamespace(
        effective_user=SimpleNamespace(id=7002),
        message=message,
    )
    context = SimpleNamespace(bot_data={})

    asyncio.run(issue.handle_issue(update, context))

    identity_lookup.assert_called_once()
    message.reply_text.assert_awaited_once()
    assert "explicitly linked" in message.reply_text.await_args.args[0]


def test_issue_classification_dataclass_is_consumed_without_type_error(monkeypatch):
    session = {}
    state_calls = []
    ephemeral_calls = []
    monkeypatch.setattr(issue, "identity_for_telegram_user", Mock(return_value=object()))
    monkeypatch.setattr(issue, "get_session", lambda _user_id: session)
    monkeypatch.setattr(
        issue,
        "set_ephemeral_issue",
        lambda user_id, value: ephemeral_calls.append((user_id, value)),
    )
    monkeypatch.setattr(
        issue,
        "set_state",
        lambda user_id, state: state_calls.append((user_id, state)),
    )

    message = SimpleNamespace(
        text="My road has been damaged",
        reply_text=AsyncMock(),
    )
    update = SimpleNamespace(
        effective_user=SimpleNamespace(id=7003),
        message=message,
    )
    context = SimpleNamespace(bot_data={"identity_link_repository": object()})

    asyncio.run(issue.handle_issue(update, context))

    assert session["category"] == "Infrastructure"
    assert session["department"] == "PWD (Public Works Department)"
    assert ephemeral_calls == [(7003, "My road has been damaged")]
    assert state_calls == [(7003, issue.WAITING_FOR_DOCUMENT)]
    message.reply_text.assert_awaited_once()
