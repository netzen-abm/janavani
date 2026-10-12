def test_polling_restart_does_not_drop_pending_updates(monkeypatch, capsys):
    import src.bot_telegram as runtime

    class FakeApplication:
        def __init__(self):
            self.polling_kwargs = None

        def run_polling(self, **kwargs):
            self.polling_kwargs = kwargs

    fake_application = FakeApplication()
    monkeypatch.setattr(runtime.Config, "TELEGRAM_BOT_TOKEN", "test-token")
    monkeypatch.setattr(runtime, "build_application", lambda *, token: fake_application)

    runtime.main()

    assert fake_application.polling_kwargs == {"drop_pending_updates": False}
