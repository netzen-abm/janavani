"""Telegram adapter for the shared channel-neutral transport contract."""

from __future__ import annotations

from typing import Any, Mapping

from src.platform.transport import TransportMessage, TransportResult


class TelegramTransportAdapter:
    """Translate Telegram-native events without owning Janavani business logic."""

    name = "telegram"

    def health(self) -> Mapping[str, Any]:
        return {"transport": self.name, "configured": True}

    def receive(self, native_event: Any) -> TransportMessage | None:
        message = getattr(native_event, "effective_message", None)
        if message is None:
            return None

        actor = getattr(message, "from_user", None)
        actor_ref = str(getattr(actor, "id", "")) or None
        chat = getattr(message, "chat", None)
        conversation_id = str(getattr(chat, "id", "")) or None
        message_id = str(getattr(message, "message_id", ""))
        text = getattr(message, "text", None)

        return TransportMessage(
            transport=self.name,
            message_id=message_id,
            conversation_id=conversation_id,
            actor_ref=actor_ref,
            text=text,
        )

    def send(self, message: TransportMessage) -> TransportResult:
        """Return an explicit unsupported state until provider delivery is wired.

        This prevents the adapter from claiming successful delivery without a
        real Telegram API acknowledgement.
        """
        return TransportResult(
            status="unsupported",
            message_id=message.message_id,
            error_code="TELEGRAM_DELIVERY_NOT_WIRED",
            retryable=False,
        )
