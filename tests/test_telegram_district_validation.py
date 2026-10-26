import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from conversation.constants import WAITING_FOR_OFFICE
from conversation.steps import district


@pytest.mark.parametrize("value", ["", " ", "1", "!!!", "x" * 101])
def test_district_rejects_unusable_input_without_advancing(monkeypatch, value):
    user_id = 54321
    session = {}
    set_state = SimpleNamespace(call=[])
    monkeypatch.setattr(district, "get_session", lambda _user_id: session)
    monkeypatch.setattr(
        district,
        "set_state",
        lambda _user_id, state: set_state.call.append(state),
    )

    message = SimpleNamespace(text=value, reply_text=AsyncMock())
    update = SimpleNamespace(
        effective_user=SimpleNamespace(id=user_id),
        message=message,
    )

    asyncio.run(district.handle_district(update, SimpleNamespace()))

    assert session == {}
    assert set_state.call == []
    message.reply_text.assert_awaited_once()


def test_district_records_input_as_unverified_and_advances(monkeypatch):
    user_id = 54322
    session = {}
    states = []
    monkeypatch.setattr(district, "get_session", lambda _user_id: session)
    monkeypatch.setattr(
        district,
        "set_state",
        lambda _user_id, state: states.append(state),
    )

    message = SimpleNamespace(text="Ernakulam", reply_text=AsyncMock())
    update = SimpleNamespace(
        effective_user=SimpleNamespace(id=user_id),
        message=message,
    )

    asyncio.run(district.handle_district(update, SimpleNamespace()))

    assert session["district"] == "Ernakulam"
    assert states == [WAITING_FOR_OFFICE]
    message.reply_text.assert_awaited_once()
    assert "not yet been verified" in message.reply_text.await_args.args[0]
