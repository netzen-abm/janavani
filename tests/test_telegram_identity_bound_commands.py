from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_telegram_rate_command_uses_canonical_identity_link_repository():
    source = (ROOT / "src" / "commands" / "rate.py").read_text(encoding="utf-8")

    assert 'bot_data.get("identity_link_repository")' in source
    assert "identity_for_telegram_user(" in source
    assert "links=links" in source


def test_telegram_rate_command_does_not_resolve_identity_without_links():
    source = (ROOT / "src" / "commands" / "rate.py").read_text(encoding="utf-8")

    assert "identity_for_telegram_user(update.effective_user.id)" not in source


def test_telegram_check_command_uses_canonical_identity_link_repository():
    source = (ROOT / "src" / "commands" / "check.py").read_text(encoding="utf-8")

    assert 'links = context.application.bot_data.get("identity_link_repository")' in source
    assert "identity_for_telegram_user(user_id, links=links)" in source


def test_telegram_rate_usage_is_concise_and_includes_valid_example():
    source = (ROOT / "src" / "commands" / "rate.py").read_text(encoding="utf-8")

    assert "/rate <office_id> <1-5> <issue>" in source
    assert "/rate KL-TVM-01 2 Aadhaar update delayed" in source
    assert "1 Very poor" in source
    assert "5 Excellent" in source
    assert "Very Poor\\n\\n2 = Poor" not in source


def test_telegram_rate_handler_uses_one_canonical_feedback_capability():
    source = (ROOT / "src" / "commands" / "rate.py").read_text(encoding="utf-8")

    assert 'bot_data.get(\n            "accountability_feedback_capability"' in source
    assert "feedback_capability.record(" in source
    assert "save_rating(" not in source
