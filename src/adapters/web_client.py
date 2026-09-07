import logging
import os
from typing import Any, Dict, Optional

import requests

logger = logging.getLogger("janavani.adapters.web_client")


class JanavaniAIWebClient:
    """Consume the decoupled Janavani AI service from a trusted server-side adapter."""

    def __init__(
        self,
        base_url: str | None = None,
        interface_token: str | None = None,
    ) -> None:
        resolved_base_url = base_url or os.getenv("JANAVANI_AI_BASE_URL", "https://janavani.internal")
        resolved_token = interface_token or os.getenv("WEB_INTERFACE_TOKEN")
        if not resolved_token:
            raise ValueError("WEB_INTERFACE_TOKEN is required for the server-side AI web adapter")

        self.base_url = f"{resolved_base_url.rstrip('/')}/api/v1/agent"
        self.headers = {
            "X-Janavani-Interface-Token": resolved_token,
            "Content-Type": "application/json",
        }

    def request_document_draft(self, citizen_text: str) -> Optional[Dict[str, Any]]:
        """Send citizen issue text to the isolated AI core for processing."""
        url = f"{self.base_url}/draft"
        payload = {"citizen_raw_input": citizen_text}

        try:
            response = requests.post(url, json=payload, headers=self.headers, timeout=30)
            if response.status_code == 200:
                return response.json()
            logger.error(
                "Web interface submission rejected with status code: %s",
                response.status_code,
            )
        except requests.RequestException as connection_error:
            logger.error(
                "Web interface failed to establish connection with AI Gateway: %s",
                connection_error,
            )
        return None
