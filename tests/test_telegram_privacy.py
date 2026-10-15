import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

from src.commands.privacy import privacy


def test_privacy_command_explains_transport_and_cancellation_limits():
    message = SimpleNamespace(reply_text=AsyncMock())
    update = SimpleNamespace(effective_message=message)

    asyncio.run(privacy(update, SimpleNamespace()))

    message.reply_text.assert_awaited_once()
    text = message.reply_text.await_args.args[0]
    assert "Telegram receives messages you send to this bot" in text
    assert "Use /cancel to clear the current in-memory workflow" in text
    assert "does not delete Telegram messages" in text
    assert "A pairing code is not a completed account link" in text
    assert "does not submit a complaint to an authority" in text
