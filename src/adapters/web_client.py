"""Authenticated AI client for the web interface."""
import logging
from typing import Dict, Optional

from src.adapters.agent_client import JanavaniAgentClient

logger = logging.getLogger("janavani.adapters.web_client")


class JanavaniAIWebClient:
    """Connect web handlers to the shared AI-agent transport."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        interface_token: Optional[str] = None,
    ) -> None:
        self._client = JanavaniAgentClient(
            interface_name="Web",
            token_env_var="JANAVANI_WEB_INTERFACE_TOKEN",
            logger=logger,
            base_url=base_url,
            interface_token=interface_token,
        )

    def request_document_draft(self, citizen_text: str) -> Optional[Dict]:
        """Request a draft through the protected agent endpoint."""
        return self._client.request_document_draft(citizen_text)
