import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

from src.bot_telegram import _set_bot_commands
from src.web.telegram_webhook_app import _webhook_commands


def test_startup_publishes_unique_discoverable_bot_commands():
    set_my_commands = AsyncMock()
    application = SimpleNamespace(
        bot=SimpleNamespace(set_my_commands=set_my_commands)
    )

    asyncio.run(_set_bot_commands(application))

    set_my_commands.assert_awaited_once()
    commands = set_my_commands.await_args.args[0]
    names = [command.command for command in commands]
    assert len(names) == len(set(names))
    assert {
        "start",
        "help",
        "complaint",
        "search",
        "check",
        "cases",
        "pair",
        "privacy",
        "cancel",
        "rate",
    } == set(names)
    assert "confirmation is required" in next(
        command.description for command in commands if command.command == "pair"
    )
    assert "in-memory workflow" in next(
        command.description for command in commands if command.command == "cancel"
    )



def test_polling_and_webhook_publish_identical_command_menus():
    set_my_commands = AsyncMock()
    application = SimpleNamespace(
        bot=SimpleNamespace(set_my_commands=set_my_commands)
    )
    asyncio.run(_set_bot_commands(application))

    polling = set_my_commands.await_args.args[0]
    webhook = _webhook_commands()
    assert [(c.command, c.description) for c in polling] == [
        (c.command, c.description) for c in webhook
    ]
    names = {command.command for command in webhook}
    assert "cases" in names
    assert "test complaint workflow" not in " ".join(
        command.description for command in webhook
    )
