import asyncio
from pathlib import Path
from types import SimpleNamespace


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

    assert "links = context.application.bot_data.get(\"identity_link_repository\")" in source
    assert "identity_for_telegram_user(user_id, links=links)" in source


def test_telegram_check_renders_recent_activity_without_private_notes(monkeypatch):
    import src.commands.check as check_module

    class Event:
        event_type = SimpleNamespace(value="case_created")
        occurred_at = "2026-10-22T10:00:00Z"
        notes = "private citizen narrative"

    class Case:
        case_id = "case-123"
        status = SimpleNamespace(value="review")
        evidence_refs = ["evidence-1"]
        document_refs = ["document-1"]
        events = [Event()]

    messages = []

    class Message:
        async def reply_text(self, text):
            messages.append(text)

    update = SimpleNamespace(
        effective_user=SimpleNamespace(id=7),
        message=Message(),
    )
    context = SimpleNamespace(args=["case-123"])

    monkeypatch.setattr(check_module, "_case_capability", lambda context: object())
    monkeypatch.setattr(check_module, "_owned_case", lambda *args: Case())

    asyncio.run(check_module.check(update, context))

    assert messages and "case_created" in messages[0]
    assert "2026-10-22T10:00:00Z" in messages[0]
    assert "Evidence references: 1" in messages[0]
    assert "Document references: 1" in messages[0]
    assert "private citizen narrative" not in messages[0]


def test_telegram_cases_command_lists_only_owned_metadata(monkeypatch):
    import src.commands.check as check_module

    class Case:
        case_id = "case-owned-1"
        case_type = "complaint"
        status = "review"
        evidence_count = 1
        document_count = 1
        narrative = "private citizen narrative"

    messages = []

    class Message:
        async def reply_text(self, text):
            messages.append(text)

    class Capability:
        def list_owned(self, *, identity, limit):
            assert limit == 10
            return [Case()]

    monkeypatch.setattr(check_module, "_case_capability", lambda context: Capability())
    monkeypatch.setattr(check_module, "_telegram_identity", lambda update, context: object())
    update = SimpleNamespace(message=Message())
    asyncio.run(check_module.cases(update, SimpleNamespace()))

    assert messages and "case-owned-1" in messages[0]
    assert "review" in messages[0]
    assert "private citizen narrative" not in messages[0]
