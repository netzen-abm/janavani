from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_telegram_rate_command_uses_canonical_identity_link_repository():
    source = (ROOT / "src" / "commands" / "rate.py").read_text(encoding="utf-8")

    assert "create_surface_case_composition" in source
    assert "composition.identity_link_repository" in source
    assert "identity_for_telegram_user(" in source
    assert "links=composition.identity_link_repository" in source


def test_telegram_rate_command_does_not_resolve_identity_without_links():
    source = (ROOT / "src" / "commands" / "rate.py").read_text(encoding="utf-8")

    assert "identity_for_telegram_user(update.effective_user.id)" not in source


def test_telegram_check_command_uses_canonical_identity_link_repository():
    source = (ROOT / "src" / "commands" / "check.py").read_text(encoding="utf-8")

    assert "links = context.application.bot_data.get(\"identity_link_repository\")" in source
    assert "identity_for_telegram_user(user_id, links=links)" in source
