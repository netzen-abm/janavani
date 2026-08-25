from src.platform.transport import TransportMessage, TransportResult


def test_transport_message_is_channel_neutral() -> None:
    message = TransportMessage(
        transport="telegram",
        message_id="msg-1",
        conversation_id="chat-1",
        text="help",
    )

    assert message.transport == "telegram"
    assert message.text == "help"
    assert message.attachments == ()


def test_transport_result_does_not_equate_acceptance_with_delivery() -> None:
    result = TransportResult(
        status="accepted",
        message_id="msg-1",
        retryable=False,
    )

    assert result.status == "accepted"
    assert result.status != "delivered"
