import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

from telegram.ext import CommandHandler
from commands.start import help_command, start
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
        "account",
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


def test_application_lifecycle_starts_and_stops_expiry_cleanup_task():
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


def test_start_and_help_have_distinct_citizen_facing_content():
    message = SimpleNamespace(reply_text=AsyncMock())
    update = SimpleNamespace(message=message, effective_message=message)

    asyncio.run(start(update, SimpleNamespace()))
    welcome = message.reply_text.await_args.args[0]
    message.reply_text.reset_mock()

    asyncio.run(help_command(update, SimpleNamespace()))
    help_text = message.reply_text.await_args.args[0]

    assert welcome != help_text
    assert "Welcome to Janavani" in welcome
    assert "/search <department> <location>" in help_text
    assert "does not submit anything automatically" in welcome
    assert "Volunteer in coding" in help_text
    assert "Malayalam translation is not enabled yet" in help_text


def test_runtime_registers_the_real_help_handler(monkeypatch):
    import src.bot_telegram as runtime

    composition = SimpleNamespace(
        case_repository=object(),
        case_capability=object(),
        civic_action_capability=object(),
        consent_repository=object(),
        evidence_capability=object(),
        authority_capability=object(),
        identity_link_repository=object(),
        provider_composition=SimpleNamespace(provider_for=lambda _domain: "memory"),
        civic_action_vertical_slice=object(),
        consent_capability=object(),
    )
    monkeypatch.setattr(runtime.Config, "TELEGRAM_BOT_TOKEN", "synthetic-test-token")
    monkeypatch.setattr(runtime, "validate_runtime_configuration", lambda: None)
    monkeypatch.setattr(runtime, "create_surface_case_composition", lambda: composition)
    monkeypatch.setattr(runtime, "create_accountability_feedback_repository", lambda **_kwargs: object())
    monkeypatch.setattr(runtime, "create_telegram_generation_dependencies", lambda **_kwargs: object())

    application = runtime.build_application()
    handlers = [handler for group in application.handlers.values() for handler in group]
    help_handler = next(
        handler for handler in handlers
        if isinstance(handler, CommandHandler) and "help" in handler.commands
    )
    assert help_handler.callback is help_command


def test_empty_authority_search_message_does_not_overstate_directory_coverage():
    from commands.search import _render

    message = _render([])
    assert "No verified authority match" in message
    assert "directory may be incomplete" in message
    assert "does not prove" in message
    assert "does not file or submit" in message
