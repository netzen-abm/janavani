import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

from src.commands.account import account
from src.identity.linking import InMemoryExternalIdentityLinkRepository


class _ProviderComposition:
    def provider_for(self, name):
        assert name == "external_identity_links"
        return "postgres"


class _Composition:
    provider_composition = _ProviderComposition()

    def __init__(self):
        self.identity_link_repository = InMemoryExternalIdentityLinkRepository()


def _context(composition):
    return SimpleNamespace(application=SimpleNamespace(bot_data={
        "surface_case_composition": composition,
    }))


def _update(*, user_id=98765, chat_type="private"):
    message = SimpleNamespace(reply_text=AsyncMock())
    return (
        SimpleNamespace(
            effective_user=SimpleNamespace(id=user_id),
            effective_chat=SimpleNamespace(type=chat_type),
            effective_message=message,
        ),
        message,
    )


def test_account_registration_is_explicit_and_creates_opaque_verified_identity():
    composition = _Composition()
    update, message = _update()

    asyncio.run(account(update, _context(composition)))

    saved = composition.identity_link_repository.find("telegram", "98765")
    assert saved is not None
    assert saved.verified is True
    assert saved.provider == "telegram"
    assert saved.authentication_method == "telegram_bot_update"
    assert saved.principal_id.startswith("janavani:citizen:")
    assert "98765" not in saved.principal_id
    reply = message.reply_text.await_args.args[0]
    assert "account is ready" in reply
    assert "does not submit" in reply


def test_existing_telegram_account_is_not_replaced_or_duplicated():
    composition = _Composition()
    update, message = _update()
    asyncio.run(account(update, _context(composition)))
    original = composition.identity_link_repository.find("telegram", "98765")

    second_update, second_message = _update()
    asyncio.run(account(second_update, _context(composition)))
    again = composition.identity_link_repository.find("telegram", "98765")

    assert again == original
    assert "already active" in second_message.reply_text.await_args.args[0]


def test_account_registration_is_private_chat_only():
    composition = _Composition()
    update, message = _update(chat_type="group")

    asyncio.run(account(update, _context(composition)))

    assert composition.identity_link_repository.find("telegram", "98765") is None
    assert "private chat" in message.reply_text.await_args.args[0]


def test_account_registration_fails_closed_without_postgres_identity_store():
    composition = _Composition()

    class MemoryOnlyProviders:
        def provider_for(self, name):
            return "memory"

    composition.provider_composition = MemoryOnlyProviders()
    update, message = _update()

    asyncio.run(account(update, _context(composition)))

    assert composition.identity_link_repository.find("telegram", "98765") is None
    assert "No account was created" in message.reply_text.await_args.args[0]
