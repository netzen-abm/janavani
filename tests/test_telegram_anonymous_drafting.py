import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

import src.conversation.steps.issue as issue_step


def test_unlinked_telegram_user_gets_complaint_and_rti_drafts_without_case_creation(monkeypatch):
    narrative = (
        "The road is broken and unsafe. Please repair it and provide copies "
        "of the tender and work order."
    )
    monkeypatch.setattr(
        issue_step,
        "identity_for_telegram_user",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(PermissionError("not linked")),
    )
    message = SimpleNamespace(
        text=narrative,
        reply_text=AsyncMock(),
        reply_document=AsyncMock(),
    )
    update = SimpleNamespace(
        effective_user=SimpleNamespace(id=123456),
        message=message,
    )
    context = SimpleNamespace(bot_data={"identity_link_repository": None})

    asyncio.run(issue_step.handle_issue(update, context))

    message.reply_document.assert_not_awaited()
    replies = [call.args[0] for call in message.reply_text.await_args_list]
    assert any("No account is needed" in reply for reply in replies)
    assert any("Draft 1 of 2" in reply for reply in replies)
    assert any("road is broken" in reply for reply in replies)
    assert issue_step.user_states[123456] == "WAITING_FOR_ANONYMOUS_REVIEW"
    from conversation.session import get_ephemeral_anonymous_drafts
    drafts = get_ephemeral_anonymous_drafts(123456)
    assert drafts is not None and [draft.document_type for draft in drafts] == ["complaint", "rti"]


def test_unlinked_telegram_user_with_short_narrative_is_prompted_to_add_detail(monkeypatch):
    monkeypatch.setattr(
        issue_step,
        "identity_for_telegram_user",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(PermissionError("not linked")),
    )
    message = SimpleNamespace(
        text="hi",
        reply_text=AsyncMock(),
        reply_document=AsyncMock(),
    )
    update = SimpleNamespace(effective_user=SimpleNamespace(id=123457), message=message)
    context = SimpleNamespace(bot_data={"identity_link_repository": None})

    asyncio.run(issue_step.handle_issue(update, context))

    message.reply_text.assert_awaited_once()
    message.reply_document.assert_not_awaited()

def test_anonymous_draft_correction_replaces_text_without_export(monkeypatch):
    from conversation.constants import WAITING_FOR_ANONYMOUS_REVIEW
    from conversation.session import (
        clear_session, get_ephemeral_anonymous_drafts, set_ephemeral_anonymous_drafts,
        set_ephemeral_issue, get_session,
    )
    from conversation.state import set_state
    from src.capabilities.anonymous_civic_drafting import build_anonymous_drafts

    user_id = 123458
    clear_session(user_id)
    set_ephemeral_issue(user_id, "The road has been damaged for months.")
    drafts = build_anonymous_drafts("The road has been damaged for months.")
    set_ephemeral_anonymous_drafts(user_id, drafts)
    get_session(user_id)["anonymous_draft_index"] = 0
    set_state(user_id, WAITING_FOR_ANONYMOUS_REVIEW)
    message = SimpleNamespace(
        text="The road outside the school has been damaged since June. Please inspect and repair it.",
        reply_text=AsyncMock(),
        reply_document=AsyncMock(),
    )
    update = SimpleNamespace(
        callback_query=None,
        effective_user=SimpleNamespace(id=user_id),
        effective_message=message,
    )
    context = SimpleNamespace(bot_data={})

    from src.conversation.steps.anonymous_review import handle_anonymous_review
    asyncio.run(handle_anonymous_review(update, context))

    revised = get_ephemeral_anonymous_drafts(user_id)
    assert revised[0].body == message.text
    message.reply_document.assert_not_awaited()
    message.reply_text.assert_awaited_once()


def test_anonymous_format_selection_exports_only_selected_format(monkeypatch):
    from conversation.constants import WAITING_FOR_ANONYMOUS_FORMAT
    from conversation.session import (
        clear_session, set_ephemeral_anonymous_drafts, set_ephemeral_issue,
        get_session,
    )
    from conversation.state import set_state
    from src.capabilities.anonymous_civic_drafting import build_anonymous_drafts
    from src.conversation.steps import anonymous_review

    user_id = 123459
    clear_session(user_id)
    set_ephemeral_issue(user_id, "The streetlight has been broken for three nights.")
    drafts = build_anonymous_drafts("The streetlight has been broken for three nights.")
    set_ephemeral_anonymous_drafts(user_id, drafts)
    get_session(user_id)["anonymous_draft_index"] = 0
    set_state(user_id, WAITING_FOR_ANONYMOUS_FORMAT)

    sent = []
    async def reply_document(**kwargs):
        sent.append(kwargs["document"].filename)
    message = SimpleNamespace(reply_document=AsyncMock(side_effect=reply_document), reply_text=AsyncMock())
    query = SimpleNamespace(
        from_user=SimpleNamespace(id=user_id),
        data="anon:pdf",
        message=message,
        answer=AsyncMock(),
        edit_message_text=AsyncMock(),
    )
    update = SimpleNamespace(callback_query=query, effective_user=None, effective_message=message, message=None)
    monkeypatch.setattr(
        anonymous_review, "render_anonymous_draft",
        lambda draft, fmt: (b"pdf bytes", "application/pdf", "pdf"),
    )

    asyncio.run(anonymous_review.handle_anonymous_review(update, SimpleNamespace(bot_data={})))

    assert sent == [f"janavani-{drafts[0].document_type}.pdf"]
    assert all(not name.endswith(".docx") for name in sent)
    assert query.answer.await_count == 1
