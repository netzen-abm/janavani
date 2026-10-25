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
    assert "If that text expires or the bot process restarts" in text
    assert "does not recover the expired narrative" in text
    assert "does not delete Telegram messages" in text
    assert "A pairing code is not a completed account link" in text
    assert "does not submit a complaint to an authority" in text

def test_privacy_command_discloses_durable_webhook_inbox_boundary():
    message = SimpleNamespace(reply_text=AsyncMock())
    update = SimpleNamespace(effective_message=message)

    asyncio.run(privacy(update, SimpleNamespace()))

    text = message.reply_text.await_args.args[0]
    assert "full Telegram update payload can be stored" in text
    assert "PostgreSQL inbox" in text
    assert "does not enforce a wall-clock deletion deadline" in text
    assert "up to 15 minutes" in text
    assert "does not mean the original webhook inbox payload is local-only" in text


def test_start_warns_about_current_webhook_retention_limit():
    from src.commands.start import start

    message = SimpleNamespace(reply_text=AsyncMock())
    update = SimpleNamespace(message=message)

    asyncio.run(start(update, SimpleNamespace()))

    text = message.reply_text.await_args.args[0]
    assert "review /privacy" in text
    assert "PostgreSQL inbox" in text
    assert "strict wall-clock deletion deadline is not yet enforced" in text
