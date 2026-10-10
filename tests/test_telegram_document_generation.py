import asyncio
from types import SimpleNamespace

from conversation.session import clear_ephemeral_issue, clear_session, get_session, set_ephemeral_issue
from conversation.state import get_state
from conversation.constants import COMPLETED
from conversation.steps import generate


class CaseContentSpy:
    def __init__(self):
        self.hydrated = None
        self.cleared = None

    def hydrate_transient_content(self, case_id, *, identity, subject, narrative):
        self.hydrated = (case_id, identity, subject, narrative)

    def clear_transient_content(self, case_id, *, identity):
        self.cleared = (case_id, identity)


class CivicActionSpy:
    def __init__(self):
        self.called = None

    def build_document(self, case_id, *, identity, document_id):
        self.called = (case_id, identity, document_id)
        return SimpleNamespace(draft="draft")


def _dependencies(case_capability, civic_action_capability, links=None):
    return generate.TelegramGenerationDependencies(
        case_repository=None,
        case_capability=case_capability,
        civic_action_capability=civic_action_capability,
        consent_capability=None,
        artifact_repository=None,
        blob_store=None,
        identity_link_repository=links,
    )


def test_artifact_builder_rehydrates_transient_issue_without_durable_case_content(monkeypatch):
    user_id = 775501
    clear_session(user_id)
    set_ephemeral_issue(user_id, "The streetlight has been out for three nights.")
    session = {
        "case_id": "case-test",
        "category": "Streetlight outage",
        "format": "pdf",
        "document_id": "doc-test",
    }
    case_content = CaseContentSpy()
    civic_action = CivicActionSpy()
    identity = object()
    monkeypatch.setattr(generate, "_identity", lambda user_id, *, links: identity)
    expected = object()
    monkeypatch.setattr(generate, "render_artifact_payload", lambda draft, fmt: expected)

    result = generate.build_canonical_complaint_artifact(
        session,
        dependencies=_dependencies(case_content, civic_action, links=object()),
        user_id=user_id,
    )

    assert result is expected
    assert case_content.hydrated == (
        "case-test", identity, "Streetlight outage",
        "The streetlight has been out for three nights.",
    )
    assert civic_action.called == ("case-test", identity, "doc-test")
    clear_ephemeral_issue(user_id)
    clear_session(user_id)


def test_generate_handler_sends_document_then_clears_transient_content(monkeypatch):
    user_id = 775502
    clear_session(user_id)
    set_ephemeral_issue(user_id, "Temporary narrative")
    session = get_session(user_id)
    session["case_id"] = "case-test"
    case_content = CaseContentSpy()
    dependencies = _dependencies(case_content, CivicActionSpy(), links=object())
    identity = SimpleNamespace(principal=SimpleNamespace(principal_id="citizen-test"))
    payload = SimpleNamespace(content=b"PDF bytes", filename="doc-test.pdf")
    monkeypatch.setattr(
        generate, "build_canonical_complaint_artifact", lambda *args, **kwargs: payload
    )
    monkeypatch.setattr(generate, "_identity", lambda user_id, *, links: identity)

    class Message:
        sent = None

        async def reply_document(self, *, document, caption):
            self.sent = (document, caption)

        async def reply_text(self, text):
            raise AssertionError(f"Unexpected error response: {text}")

    message = Message()
    update = SimpleNamespace(
        effective_user=SimpleNamespace(id=user_id), effective_message=message
    )
    context = SimpleNamespace(
        application=SimpleNamespace(bot_data={"telegram_generation_dependencies": dependencies})
    )

    asyncio.run(generate.handle_generate(update, context))

    assert message.sent is not None
    assert "has not transmitted" in message.sent[1]
    assert case_content.cleared == ("case-test", identity)
    assert get_state(user_id) == COMPLETED
    assert get_session(user_id).get("_ephemeral_issue") is None
    clear_session(user_id)



def test_telegram_runtime_and_generation_state_import_cleanly():
    from conversation.constants import WAITING_FOR_GENERATE
    from conversation.state_registry import get_handler
    import src.bot_telegram as telegram_runtime

    assert callable(telegram_runtime.main)
    assert get_handler(WAITING_FOR_GENERATE) is generate.handle_generate
