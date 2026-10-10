import asyncio
from types import SimpleNamespace

from conversation.session import clear_session, get_session
from conversation.steps.issue import handle_issue
from src.identity.linking import InMemoryExternalIdentityLinkRepository


def test_unlinked_telegram_user_gets_clear_failure_without_retaining_issue_text():
    user_id = 998877
    clear_session(user_id)
    replies = []

    async def reply_text(text):
        replies.append(text)

    update = SimpleNamespace(
        effective_user=SimpleNamespace(id=user_id),
        message=SimpleNamespace(
            text="Sensitive issue details that must not be retained",
            reply_text=reply_text,
        ),
    )
    context = SimpleNamespace(
        bot_data={"identity_link_repository": InMemoryExternalIdentityLinkRepository()}
    )

    async def run():
        await handle_issue(update, context)

    asyncio.run(run())
    session = get_session(user_id)
    assert replies and "no Case was created" in replies[0]
    assert session.get("_ephemeral_issue") is None
    assert session.get("case_id", "") == ""
    clear_session(user_id)
