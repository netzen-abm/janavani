import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

from conversation.session import clear_session, get_ephemeral_issue, get_session
from conversation.steps.issue import handle_issue
from src.identity.linking import InMemoryExternalIdentityLinkRepository


def test_unlinked_telegram_user_gets_clear_failure_without_retaining_issue_text():
    user_id = 998877
    clear_session(user_id)
    replies = []

    async def reply_text(text, **kwargs):
        replies.append(text)

    update = SimpleNamespace(
        effective_user=SimpleNamespace(id=user_id),
        message=SimpleNamespace(
            text="Sensitive issue details that must not be retained",
            reply_text=reply_text,
            reply_document=AsyncMock(),
        ),
    )
    context = SimpleNamespace(
        bot_data={"identity_link_repository": InMemoryExternalIdentityLinkRepository()}
    )

    async def run():
        await handle_issue(update, context)

    asyncio.run(run())
    session = get_session(user_id)
    assert replies and any("No account is needed" in reply for reply in replies)
    assert any("has not registered a Case" in reply for reply in replies)
    assert update.message.reply_document.await_count == 2
    assert get_ephemeral_issue(user_id) is None
    assert "_ephemeral_issue" not in session
    assert session.get("case_id", "") == ""
    clear_session(user_id)
