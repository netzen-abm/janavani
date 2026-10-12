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
