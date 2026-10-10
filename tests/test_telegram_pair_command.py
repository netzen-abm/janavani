import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

from src.commands.pair import pair


def _update(*, chat_type="private", args=None, user_id=1234):
    message = SimpleNamespace(reply_text=AsyncMock(), delete=AsyncMock())
    user = SimpleNamespace(id=user_id)
    chat = SimpleNamespace(type=chat_type)
    update = SimpleNamespace(
        effective_message=message,
        effective_user=user,
        effective_chat=chat,
    )
    context = SimpleNamespace(
        args=args or [],
        application=SimpleNamespace(bot_data={}),
    )
    return update, context, message


def test_pair_refuses_group_chat_without_claiming_code():
    update, context, message = _update(chat_type="group", args=["secret-code"])
    service = Mock()
    context.application.bot_data["identity_pairing_service"] = service

    asyncio.run(pair(update, context))

    service.claim_telegram.assert_not_called()
    message.reply_text.assert_awaited_once()
    assert "private chat" in message.reply_text.await_args.args[0]


def test_pair_requires_exactly_one_code():
    update, context, message = _update(args=[])
    context.application.bot_data["identity_pairing_service"] = Mock()

    asyncio.run(pair(update, context))

    context.application.bot_data["identity_pairing_service"].claim_telegram.assert_not_called()
    assert "Usage: /pair" in message.reply_text.await_args.args[0]


def test_pair_fails_closed_when_shared_pairing_is_not_configured():
    update, context, message = _update(args=["secret-code"])

    asyncio.run(pair(update, context))

    message.reply_text.assert_awaited_once()
    assert "not configured" in message.reply_text.await_args.args[0]


def test_pair_claims_as_authenticated_telegram_subject_and_does_not_claim_linked():
    update, context, message = _update(args=["secret-code"], user_id=98765)
    service = Mock()
    service.claim_telegram.return_value = SimpleNamespace(pairing_id="pair-ref-1")
    context.application.bot_data["identity_pairing_service"] = service

    asyncio.run(pair(update, context))

    service.claim_telegram.assert_called_once_with(
        "secret-code",
        telegram_subject="98765",
    )
    message.delete.assert_awaited_once()
    reply = message.reply_text.await_args.args[0]
    assert "NOT linked" in reply
    assert "authenticated" in reply
    assert "pair-ref-1" in reply


def test_pair_rejects_invalid_or_replayed_code_without_exposing_exception():
    update, context, message = _update(args=["secret-code"])
    service = Mock()
    service.claim_telegram.side_effect = LookupError("sensitive internal detail")
    context.application.bot_data["identity_pairing_service"] = service

    asyncio.run(pair(update, context))

    reply = message.reply_text.await_args.args[0]
    assert "invalid, expired, or already used" in reply
    assert "sensitive internal detail" not in reply
