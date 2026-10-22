import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest

from src.commands.check import cases, check


def _update_context(*, chat_type: str, args: list[str]):
    message = SimpleNamespace(reply_text=AsyncMock())
    capability = Mock()
    update = SimpleNamespace(
        message=message,
        effective_message=message,
        effective_user=SimpleNamespace(id=12345),
        effective_chat=SimpleNamespace(type=chat_type),
    )
    context = SimpleNamespace(
        args=args,
        application=SimpleNamespace(
            bot_data={"civic_case_capability": capability}
        ),
    )
    return update, context, message, capability


@pytest.mark.parametrize(
    ("handler", "args", "blocked_method"),
    [
        (cases, [], "list_owned"),
        (check, ["case-private-1"], "get_owned"),
    ],
)
@pytest.mark.parametrize("chat_type", ["group", "supergroup"])
def test_case_metadata_commands_refuse_group_chat(
    handler, args: list[str], blocked_method: str, chat_type: str
):
    update, context, message, capability = _update_context(
        chat_type=chat_type, args=args
    )

    asyncio.run(handler(update, context))

    message.reply_text.assert_awaited_once()
    assert "private chat" in message.reply_text.await_args.args[0]
    getattr(capability, blocked_method).assert_not_called()
