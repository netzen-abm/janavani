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
