import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

from src.commands.pair import pair
from src.identity.pairing import IdentityPairingService, InMemoryPairingRepository


def update_context(*, chat_type="private", args=None, service=None):
    message = SimpleNamespace(reply_text=AsyncMock(), delete=AsyncMock())
    update = SimpleNamespace(
        effective_message=message,
        effective_user=SimpleNamespace(id=12345),
        effective_chat=SimpleNamespace(type=chat_type),
    )
    context = SimpleNamespace(
        args=args or [],
        application=SimpleNamespace(bot_data={"identity_pairing_service": service}),
    )
    return update, context, message


def test_pair_command_rejects_group_chat_without_claiming_code():
    service = IdentityPairingService(InMemoryPairingRepository())
    challenge = service.issue(principal_id="citizen:test")
    update, context, message = update_context(
        chat_type="group", args=[challenge.code], service=service,
    )
    asyncio.run(pair(update, context))
    message.reply_text.assert_awaited_once()
    message.delete.assert_not_awaited()


def test_pair_command_deletes_code_message_and_claims_only_in_private_chat():
    service = IdentityPairingService(InMemoryPairingRepository())
    challenge = service.issue(principal_id="citizen:test")
    update, context, message = update_context(args=[challenge.code], service=service)
    asyncio.run(pair(update, context))
    message.delete.assert_awaited_once()
    response = message.reply_text.await_args.args[0]
    assert "not linked yet" in response
    assert challenge.code not in response
