"""Authenticated AI client for the Telegram interface."""
import logging
from typing import Dict, Optional

from src.adapters.agent_client import JanavaniAgentClient

logger = logging.getLogger("janavani.adapters.telegram_client")


class JanavaniAITelegramClient:
    """Connect Telegram handlers to the shared AI-agent transport."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        interface_token: Optional[str] = None,
    ) -> None:
        self._client = JanavaniAgentClient(
            interface_name="Telegram",
            token_env_var="JANAVANI_TELEGRAM_INTERFACE_TOKEN",
            logger=logger,
            base_url=base_url,
            interface_token=interface_token,
        )

    def request_document_draft(self, citizen_text: str) -> Optional[Dict]:
        """Request a draft through the protected agent endpoint."""
        return self._client.request_document_draft(citizen_text)

    def poll_cached_document(self, tracking_id: str) -> Optional[Dict]:
        """Retrieve an unexpired draft from temporary storage.

        This method name means checking cached document availability, not
        Telegram update polling. Telegram transport stays webhook-based.
        """
        return self._client.retrieve_document(tracking_id)
