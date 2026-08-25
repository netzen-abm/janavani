from types import SimpleNamespace

from src.adapters.telegram_transport import TelegramTransportAdapter


def test_receive_normalizes_message_without_business_logic() -> None:
    native = SimpleNamespace(
        effective_message=SimpleNamespace(
            message_id=42,
            text="hello",
            from_user=SimpleNamespace(id=7),
            chat=SimpleNamespace(id=99),
        )
    )

    message = TelegramTransportAdapter().receive(native)

    assert message is not None
    assert message.transport == "telegram"
    assert message.message_id == "42"
    assert message.actor_ref == "7"
    assert message.conversation_id == "99"
    assert message.text == "hello"


def test_non_message_event_is_ignored() -> None:
    assert TelegramTransportAdapter().receive(SimpleNamespace(effective_message=None)) is None


def test_send_does_not_claim_delivery_before_provider_wiring() -> None:
    message = TelegramTransportAdapter().receive(
        SimpleNamespace(
            effective_message=SimpleNamespace(
                message_id=42,
                text="hello",
                from_user=SimpleNamespace(id=7),
                chat=SimpleNamespace(id=99),
            )
        )
    )

    result = TelegramTransportAdapter().send(message)

    assert result.status == "unsupported"
    assert result.error_code == "TELEGRAM_DELIVERY_NOT_WIRED"
    assert result.retryable is False
