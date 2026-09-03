import logging
from typing import Any, Dict, Optional

import requests

from src.core.interface_credentials import get_interface_credential

logger = logging.getLogger("janavani.adapters.web_client")


class JanavaniAIWebClient:
    """Consume the isolated Janavani Agentic AI service from the web interface."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        interface_token: Optional[str] = None,
    ):
        self.base_url = (base_url or "https://janavani.internal").rstrip("/") + "/api/v1/agent"
        token = interface_token or get_interface_credential("JANAVANI_WEB_INTERFACE_TOKEN").value
        self.headers = {
            "X-Janavani-Interface-Token": token,
            "Content-Type": "application/json",
        }

    def request_document_draft(self, citizen_text: str) -> Optional[Dict[str, Any]]:
        """Send raw citizen issue text to the isolated AI service."""
        try:
            response = requests.post(
                f"{self.base_url}/draft",
                json={"citizen_raw_input": citizen_text},
                headers=self.headers,
                timeout=30,
            )
            if response.status_code == 200:
                return response.json()
            logger.error("Web interface submission rejected: status=%s", response.status_code)
        except requests.RequestException as exc:
            logger.error("Web interface failed to reach AI Gateway: %s", exc)
        return None
