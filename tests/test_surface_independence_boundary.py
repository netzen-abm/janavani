from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WEB_ENTRYPOINT = ROOT / "src" / "web.py"


def test_web_surface_does_not_spawn_telegram_process() -> None:
    source = WEB_ENTRYPOINT.read_text(encoding="utf-8")

    assert "subprocess.Popen" not in source
    assert "src/bot_telegram.py" not in source
    assert "START_TELEGRAM_FOR_LOCAL" not in source


def test_web_surface_documents_canonical_runtime() -> None:
    source = WEB_ENTRYPOINT.read_text(encoding="utf-8")

    assert "src.web.canonical_app:app" in source
