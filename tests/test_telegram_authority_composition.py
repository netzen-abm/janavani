from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_telegram_authority_search_uses_bootstrap_composition():
    source = (ROOT / "src" / "commands" / "search.py").read_text(encoding="utf-8")
    assert 'context.application.bot_data.get("authority_capability")' in source
    assert "create_authority_repository()" not in source
    assert "create_authority_capability(" not in source


def test_canonical_office_states_use_verified_selection_and_keep_legacy_archived():
    registry = (ROOT / "src" / "conversation" / "state_registry.py").read_text(encoding="utf-8")
    archived = ROOT / "archive" / "legacy" / "2026-10-26" / "src" / "conversation" / "steps" / "office.py"

    assert archived.is_file()
    assert "from conversation.steps.office import" not in registry
    assert "WAITING_FOR_OFFICE: handle_select_office" in registry
    assert "WAITING_FOR_OFFICE_SELECTION: handle_office_selection" in registry
