import asyncio
from types import SimpleNamespace

import pytest

from conversation.session import clear_ephemeral_issue, clear_session, get_session, set_ephemeral_issue
from conversation.state import get_state
from conversation.constants import COMPLETED, WAITING_FOR_GENERATE, WAITING_FOR_READY
from conversation.steps import generate


class CaseCapabilitySpy:
    def __init__(self, status="ready"):
        self.status = status
        self.cleared = None
        self.approved = 0

    def get_owned(self, case_id, *, identity):
        return SimpleNamespace(status=SimpleNamespace(value=self.status))

    def clear_transient_content(self, case_id, *, identity):
        self.cleared = (case_id, identity)

    def approve(self, case_id, *, identity):
        self.approved += 1
        self.status = "ready"


class DocumentReviewSpy:
    def __init__(self, draft=None):
        self.draft = draft or SimpleNamespace(
            document_id="doc-test", case_id="case-test", subject="Subject", body="Reviewed body"
        )
        self.requested = None

    def get_owned(self, document_id, *, identity):
        self.requested = (document_id, identity)
        return self.draft if document_id == self.draft.document_id else None


def _dependencies(case_capability, *, links=None, review=None):
    return generate.TelegramGenerationDependencies(
        case_repository=None,
        case_capability=case_capability,
        civic_action_capability=None,
        consent_capability=None,
        artifact_repository=None,
        blob_store=None,
        identity_link_repository=links,
        document_review_capability=review or DocumentReviewSpy(),
    )


def test_artifact_builder_requires_ready_case_and_uses_saved_draft(monkeypatch):
    user_id = 775501
    session = {"case_id": "case-test", "format": "pdf", "document_id": "doc-test"}
    case_capability = CaseCapabilitySpy(status="review")
    review = DocumentReviewSpy()
    dependencies = _dependencies(case_capability, links=object(), review=review)
    identity = object()
    monkeypatch.setattr(generate, "_identity", lambda *_args, **_kwargs: identity)
    rendered = []
    monkeypatch.setattr(generate, "render_artifact_payload", lambda draft, fmt: rendered.append((draft, fmt)) or "payload")

    with pytest.raises(PermissionError, match="Final Case readiness"):
        generate.build_canonical_complaint_artifact(
            session, dependencies=dependencies, user_id=user_id
        )
    assert review.requested is None

    case_capability.status = "ready"
    result = generate.build_canonical_complaint_artifact(
        session, dependencies=dependencies, user_id=user_id
    )
    assert result == "payload"
    assert review.requested == ("doc-test", identity)
    assert rendered == [(review.draft, generate.DocumentFormat.PDF)]


def test_generate_handler_sends_document_then_clears_transient_content(monkeypatch):
    user_id = 775502
    clear_session(user_id)
    set_ephemeral_issue(user_id, "Temporary narrative")
    session = get_session(user_id)
    session["case_id"] = "case-test"
    session["document_id"] = "doc-test"
    case_capability = CaseCapabilitySpy()
    dependencies = _dependencies(case_capability, links=object())
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
    assert case_capability.cleared == ("case-test", identity)
    assert get_state(user_id) == COMPLETED
    assert get_session(user_id).get("_ephemeral_issue") is None
    clear_session(user_id)


def test_telegram_runtime_and_readiness_states_import_cleanly():
    from conversation.state_registry import get_handler
    from conversation.steps.consent import handle_ready_confirmation
    import src.bot_telegram as telegram_runtime

    assert callable(telegram_runtime.main)
    assert get_handler(WAITING_FOR_READY) is handle_ready_confirmation
    assert get_handler(WAITING_FOR_GENERATE) is handle_ready_confirmation


def test_ready_confirmation_is_required_before_generation(monkeypatch):
    from conversation.steps import consent

    user_id = 775503
    clear_session(user_id)
    get_session(user_id)["case_id"] = "case-ready-test"
    case_capability = CaseCapabilitySpy(status="review")
    dependencies = _dependencies(case_capability, links=object())
    identity = object()
    called = []
    monkeypatch.setattr(consent, "_identity", lambda *_args, **_kwargs: identity)
    async def fake_generate(*_args, **_kwargs):
        called.append("generated")

    monkeypatch.setattr(consent, "handle_generate", fake_generate)

    class Message:
        text = "READY"
        async def reply_text(self, text): pass

    update = SimpleNamespace(
        effective_user=SimpleNamespace(id=user_id),
        effective_message=Message(),
    )
    context = SimpleNamespace(
        application=SimpleNamespace(bot_data={"telegram_generation_dependencies": dependencies})
    )
    asyncio.run(consent.handle_ready_confirmation(update, context))
    assert case_capability.approved == 1
    assert called == ["generated"]
    assert get_state(user_id) == WAITING_FOR_GENERATE
    clear_session(user_id)
