import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

from src.bot_telegram import _post_init, _set_bot_commands, _stop_ephemeral_issue_cleanup
from src.commands.catalogue import telegram_bot_commands


def test_startup_publishes_unique_discoverable_bot_commands():
    set_my_commands = AsyncMock()
    application = SimpleNamespace(
        bot=SimpleNamespace(set_my_commands=set_my_commands)
    )

    asyncio.run(_set_bot_commands(application))

    set_my_commands.assert_awaited_once()
    commands = set_my_commands.await_args.args[0]
    assert commands == telegram_bot_commands()
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


def test_polling_runtime_starts_and_stops_expiry_cleanup_task():
    application = SimpleNamespace(
        bot=SimpleNamespace(set_my_commands=AsyncMock()),
        bot_data={},
    )

    async def run_lifecycle():
        await _post_init(application)
        task = application.bot_data.get("janavani_ephemeral_issue_cleanup")
        assert task is not None and not task.done()
        await _stop_ephemeral_issue_cleanup(application)
        assert task.cancelled()

    asyncio.run(run_lifecycle())
