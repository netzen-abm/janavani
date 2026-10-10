from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_telegram_authority_search_uses_bootstrap_composition():
    source = (ROOT / "src" / "commands" / "search.py").read_text(encoding="utf-8")
    assert 'context.application.bot_data.get("authority_capability")' in source
    assert "create_authority_repository()" not in source
    assert "create_authority_capability(" not in source
