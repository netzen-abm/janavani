from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_rate_command_consumes_bot_composition_instead_of_composing_dependencies():
    source = (ROOT / "src" / "commands" / "rate.py").read_text(encoding="utf-8")

    assert "create_surface_case_composition" not in source
    assert "create_accountability_feedback_repository" not in source
    assert 'bot_data.get("accountability_feedback_capability")' in source
    assert 'bot_data.get("identity_link_repository")' in source


def test_telegram_bootstrap_composes_feedback_capability_once():
    source = (ROOT / "src" / "bot_telegram.py").read_text(encoding="utf-8")

    assert "create_accountability_feedback_repository" in source
    assert 'application.bot_data["accountability_feedback_capability"]' in source
