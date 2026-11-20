import asyncio

from types import SimpleNamespace
from unittest.mock import AsyncMock

from conversation.constants import (
    COMPLETED,
    WAITING_FOR_CIVIC_DRAFT_CHOICE,
    WAITING_FOR_CIVIC_DRAFT_EXISTING,
    WAITING_FOR_CIVIC_DRAFT_ISSUE,
    WAITING_FOR_CIVIC_DRAFT_JURISDICTION,
    WAITING_FOR_CIVIC_DRAFT_RECORDS,
    WAITING_FOR_CIVIC_DRAFT_TYPE,
)
from conversation.session import get_ephemeral_civic_draft, user_sessions
from conversation.state import get_state, set_state, user_states
from src.commands import ai_draft as ai_command
from src.conversation.steps import civic_draft as draft_step


def _update(user_id: int, text: str = "", *, chat_type: str = "private"):
    message = SimpleNamespace(
        text=text,
        chat=SimpleNamespace(type=chat_type),
        reply_text=AsyncMock(),
        reply_document=AsyncMock(),
    )
    return SimpleNamespace(
        effective_user=SimpleNamespace(id=user_id),
        effective_message=message,
    ), message


def _reset(user_id: int):
    user_sessions.pop(user_id, None)
    user_states.pop(user_id, None)


def test_ai_draft_command_starts_with_template_choice_and_no_remote_call():
    user_id = 88001
    _reset(user_id)
    update, message = _update(user_id)
    context = SimpleNamespace(args=[], application=SimpleNamespace(bot_data={}))

    asyncio.run(ai_command.ai_draft_command(update, context))

    assert get_state(user_id) == WAITING_FOR_CIVIC_DRAFT_TYPE
    notice = message.reply_text.await_args.args[0]
    assert "not saved to a Janavani Case or submitted" in notice
    assert "24-hour expiry window" in notice
    assert "encrypted payloads may remain until cleanup resumes" in notice
    assert "Remote AI improvement is temporarily disabled" in notice
    buttons = message.reply_text.await_args.kwargs["reply_markup"].inline_keyboard
    callback_data = {button.callback_data for row in buttons for button in row}
    assert "civicdraft:type:rti.records" in callback_data
    assert "civicdraft:type:complaint.general" in callback_data
    assert "civicdraft:type:administrative.evidence-demand" in callback_data


def test_rti_flow_collects_authority_and_existing_records_before_preview(monkeypatch):
    user_id = 88002
    _reset(user_id)
    update, _ = _update(user_id)
    context = SimpleNamespace(args=[], application=SimpleNamespace(bot_data={}))
    asyncio.run(ai_command.ai_draft_command(update, context))

    callback_message = SimpleNamespace(
        chat=SimpleNamespace(type="private"),
        reply_text=AsyncMock(),
        reply_document=AsyncMock(),
    )
    query = SimpleNamespace(
        data="civicdraft:type:rti.records",
        from_user=SimpleNamespace(id=user_id),
        message=callback_message,
        answer=AsyncMock(),
    )
    asyncio.run(ai_command.handle_civic_draft_callback(
        SimpleNamespace(callback_query=query), context
    ))
    assert get_state(user_id) == WAITING_FOR_CIVIC_DRAFT_ISSUE

    def send(text):
        update, message = _update(user_id, text)
        asyncio.run(draft_step.handle_civic_draft_text(update, context))
        return message

    send("I request records concerning the road-repair work.")
    assert get_state(user_id) == WAITING_FOR_CIVIC_DRAFT_JURISDICTION
    send("Kerala State public authority")
    assert get_state(user_id) == WAITING_FOR_CIVIC_DRAFT_RECORDS
    send("Existing work order for April\nExisting inspection report")
    assert get_state(user_id) == WAITING_FOR_CIVIC_DRAFT_EXISTING

    class FakeWorkflow:
        def preview(self, request, **kwargs):
            assert request.template_id == "rti.records"
            assert request.jurisdiction == "Kerala State public authority"
            assert request.requested_documents == (
                "Existing work order for April", "Existing inspection report"
            )
            assert kwargs == {}
            return {
                "template_id": request.template_id,
                "template_version": 1,
                "draft_body": "RTI draft preview",
                "ai_used": False,
                "ai_status": "not_requested",
            }

    monkeypatch.setattr(draft_step, "CivicDraftPreviewWorkflow", FakeWorkflow)
    message = send("-")
    assert get_state(user_id) == WAITING_FOR_CIVIC_DRAFT_CHOICE
    message.reply_document.assert_awaited_once()
    assert message.reply_document.await_args.kwargs["reply_markup"] is not None
    transient = get_ephemeral_civic_draft(user_id)
    assert transient["requested_documents"] == [
        "Existing work order for April", "Existing inspection report"
    ]


def test_legacy_remote_ai_callback_fails_closed_and_clears_transient_content(monkeypatch):
    user_id = 88003
    _reset(user_id)
    from conversation.session import set_ephemeral_civic_draft
    set_ephemeral_civic_draft(user_id, {
        "template_id": "complaint.general",
        "issue": "The local road is damaged.",
        "subject": "",
        "existing_draft": "Please repair this road.",
        "jurisdiction": "",
        "requested_documents": [],
    })
    set_state(user_id, WAITING_FOR_CIVIC_DRAFT_CHOICE)

    message = SimpleNamespace(
        chat=SimpleNamespace(type="private"),
        reply_text=AsyncMock(),
        reply_document=AsyncMock(),
    )
    query = SimpleNamespace(
        data="civicdraft:ai",
        from_user=SimpleNamespace(id=user_id),
        message=message,
        answer=AsyncMock(),
    )
    context = SimpleNamespace(application=SimpleNamespace(bot_data={
        "identity_link_repository": object(),
    }))

    asyncio.run(ai_command.handle_civic_draft_callback(
        SimpleNamespace(callback_query=query), context
    ))

    message.reply_text.assert_awaited_once()
    notice = message.reply_text.await_args.args[0]
    assert "temporarily disabled" in notice
    assert "No issue narrative or pasted draft was sent" in notice
    message.reply_document.assert_not_awaited()
    assert get_ephemeral_civic_draft(user_id) is None
    assert get_state(user_id) == COMPLETED


def test_ai_draft_command_rejects_group_chat_before_collecting_content():
    user_id = 88004
    _reset(user_id)
    update, message = _update(user_id, chat_type="group")
    context = SimpleNamespace(args=[], application=SimpleNamespace(bot_data={}))

    asyncio.run(ai_command.ai_draft_command(update, context))

    assert get_state(user_id) != WAITING_FOR_CIVIC_DRAFT_TYPE
    assert get_ephemeral_civic_draft(user_id) is None
    assert "only in a private chat" in message.reply_text.await_args.args[0]


def test_draft_callback_rejects_group_chat_before_mutating_state():
    user_id = 88005
    _reset(user_id)
    set_state(user_id, WAITING_FOR_CIVIC_DRAFT_TYPE)
    message = SimpleNamespace(
        chat=SimpleNamespace(type="group"),
        reply_text=AsyncMock(),
    )
    query = SimpleNamespace(
        data="civicdraft:type:complaint.general",
        from_user=SimpleNamespace(id=user_id),
        message=message,
        answer=AsyncMock(),
    )
    context = SimpleNamespace(application=SimpleNamespace(bot_data={}))

    asyncio.run(ai_command.handle_civic_draft_callback(
        SimpleNamespace(callback_query=query), context
    ))

    assert get_state(user_id) == WAITING_FOR_CIVIC_DRAFT_TYPE
    assert get_ephemeral_civic_draft(user_id) is None
    assert "only in a private chat" in message.reply_text.await_args.args[0]


def test_legacy_remote_ai_callback_does_not_retain_transient_content_when_repeated():
    user_id = 88006
    _reset(user_id)
    from conversation.session import set_ephemeral_civic_draft

    set_ephemeral_civic_draft(user_id, {
        "template_id": "complaint.general",
        "issue": "The public drain is blocked.",
        "subject": "",
        "existing_draft": "",
        "jurisdiction": "",
        "requested_documents": [],
    })
    set_state(user_id, WAITING_FOR_CIVIC_DRAFT_CHOICE)
    message = SimpleNamespace(
        chat=SimpleNamespace(type="private"),
        reply_text=AsyncMock(),
        reply_document=AsyncMock(),
    )
    query = SimpleNamespace(
        data="civicdraft:ai",
        from_user=SimpleNamespace(id=user_id),
        message=message,
        answer=AsyncMock(),
    )
    context = SimpleNamespace(application=SimpleNamespace(bot_data={}))

    asyncio.run(ai_command.handle_civic_draft_callback(
        SimpleNamespace(callback_query=query), context
    ))

    assert get_ephemeral_civic_draft(user_id) is None
    assert get_state(user_id) == COMPLETED
    assert "temporarily disabled" in message.reply_text.await_args.args[0]
    message.reply_document.assert_not_awaited()


def test_administrative_evidence_demand_telegram_flow_collects_jurisdiction(monkeypatch):
    user_id = 88007
    _reset(user_id)
    update, _ = _update(user_id)
    context = SimpleNamespace(args=[], application=SimpleNamespace(bot_data={}))
    asyncio.run(ai_command.ai_draft_command(update, context))

    callback_message = SimpleNamespace(
        chat=SimpleNamespace(type="private"),
        reply_text=AsyncMock(),
        reply_document=AsyncMock(),
    )
    query = SimpleNamespace(
        data="civicdraft:type:administrative.evidence-demand",
        from_user=SimpleNamespace(id=user_id),
        message=callback_message,
        answer=AsyncMock(),
    )
    asyncio.run(ai_command.handle_civic_draft_callback(
        SimpleNamespace(callback_query=query), context
    ))
    assert get_state(user_id) == WAITING_FOR_CIVIC_DRAFT_ISSUE

    def send(text):
        update, message = _update(user_id, text)
        asyncio.run(draft_step.handle_civic_draft_text(update, context))
        return message

    send("The municipality has demanded a recurring sanitation levy.")
    assert get_state(user_id) == WAITING_FOR_CIVIC_DRAFT_JURISDICTION
    send("Kerala municipal authority")
    assert get_state(user_id) == WAITING_FOR_CIVIC_DRAFT_EXISTING

    class FakeWorkflow:
        def preview(self, request, **kwargs):
            assert request.template_id == "administrative.evidence-demand"
            assert request.jurisdiction == "Kerala municipal authority"
            assert kwargs == {}
            return {
                "template_id": request.template_id,
                "template_version": 1,
                "draft_body": "Administrative evidence-demand preview",
                "ai_used": False,
                "ai_status": "not_requested",
            }

    monkeypatch.setattr(draft_step, "CivicDraftPreviewWorkflow", FakeWorkflow)
    message = send("-")
    message.reply_document.assert_awaited_once()
    assert get_state(user_id) == WAITING_FOR_CIVIC_DRAFT_CHOICE
