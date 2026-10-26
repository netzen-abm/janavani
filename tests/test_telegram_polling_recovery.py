import pytest


def test_legacy_entrypoint_fails_closed_instead_of_starting_polling(monkeypatch):
    import src.bot_telegram as runtime

    monkeypatch.setattr(runtime.Config, "TELEGRAM_BOT_TOKEN", "synthetic-test-token")
    with pytest.raises(RuntimeError, match="Telegram polling is disabled"):
        runtime.main()
