import asyncio
from types import SimpleNamespace

from conversation.constants import WAITING_FOR_READY
from conversation.session import clear_session, get_session, set_ephemeral_issue
from conversation.state import get_state
from conversation.steps import consent as consent_step
from conversation.steps.generate import TelegramGenerationDependencies


def test_preparation_consent_persists_preview_without_generating_file(monkeypatch):
    user_id = 775504
    clear_session(user_id)
    session = get_session(user_id)
    session.update({
        "case_id": "case-telegram-review",
        "category": "Streetlight outage",
        "office": {"office_id": "office-verified"},
        "format": "pdf",
    })
    set_ephemeral_issue(user_id, "The streetlight has been out for three nights.")
    identity = object()
    calls = {"consent": 0, "draft": 0, "review": 0, "generated": 0}

    class CaseCapability:
        def hydrate_transient_content(self, case_id, **kwargs):
            assert case_id == session["case_id"]
            assert kwargs["narrative"] == "The streetlight has been out for three nights."

        def get_owned(self, case_id, *, identity):
            return SimpleNamespace(status=SimpleNamespace(value="draft"))

    class CivicActionSpy:
        def start_review(self, case_id, *, identity):
            calls["review"] += 1

    class ConsentCapability:
        def record_document_preparation_consent(self, case_id, **kwargs):
            calls["consent"] += 1
            assert kwargs["scope"] == "office:office-verified"

    class DraftingCapability:
        def create_draft(self, case_id, request, *, identity, document_id):
            calls["draft"] += 1
            assert request.subject == "Streetlight outage"
            assert request.issue == "The streetlight has been out for three nights."
            session["document_id"] = document_id
            return SimpleNamespace(document=SimpleNamespace(
                subject=request.subject, body="Structured draft for review."
            ))

    class AuthorityCapability:
        def require_verified_destination(self, office_id):
            assert office_id == "office-verified"

    dependencies = TelegramGenerationDependencies(
        case_repository=None,
        case_capability=CaseCapability(),
        civic_action_capability=None,
        consent_capability=ConsentCapability(),
        artifact_repository=None,
        blob_store=None,
        identity_link_repository=object(),
        letter_drafting_capability=DraftingCapability(),
        document_review_capability=None,
        civic_action_vertical_slice=CivicActionSpy(),
    )
    monkeypatch.setattr(consent_step, "_identity", lambda *_args, **_kwargs: identity)

    async def unexpected_generation(*_args, **_kwargs):
        calls["generated"] += 1
        raise AssertionError("Preparation consent must not generate or deliver the final file")

    monkeypatch.setattr(consent_step, "handle_generate", unexpected_generation)

    class Message:
        text = "YES"
        documents = []
        replies = []

        async def reply_document(self, **kwargs):
            self.documents.append(kwargs)

        async def reply_text(self, text):
            self.replies.append(text)

    message = Message()
    update = SimpleNamespace(
        effective_user=SimpleNamespace(id=user_id),
        effective_message=message,
        message=message,
        update_id=441,
    )
    context = SimpleNamespace(application=SimpleNamespace(bot_data={
        "telegram_generation_dependencies": dependencies,
        "authority_capability": AuthorityCapability(),
    }))

    asyncio.run(consent_step.handle_consent(update, context))

    assert calls == {"consent": 1, "draft": 1, "review": 1, "generated": 0}
    assert get_state(user_id) == WAITING_FOR_READY
    assert message.documents
    assert any("Reply READY" in reply for reply in message.replies)
    clear_session(user_id)
