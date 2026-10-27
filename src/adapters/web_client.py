import requests
import logging
import os
from typing import Dict, Any, Optional

logger = logging.getLogger("janavani.adapters.web_client")


class JanavaniAIWebClient:
    """Connects the web interface to the isolated Janavani AI service."""

    def __init__(self, base_url: Optional[str] = None, interface_token: Optional[str] = None):
        configured_base_url = base_url or os.getenv(
            "JANAVANI_AGENT_BASE_URL", "https://janavani.internal"
        )
        self.base_url = f"{configured_base_url.rstrip('/')}/api/v1/agent"
        self.interface_token = interface_token or os.getenv(
            "JANAVANI_WEB_INTERFACE_TOKEN"
        )
        self.headers = {"Content-Type": "application/json"}
        if self.interface_token:
            self.headers["X-Janavani-Interface-Token"] = self.interface_token

    def request_document_draft(self, citizen_text: str) -> Optional[Dict[str, Any]]:
        """Send citizen issue text to the isolated AI core."""
        if not self.interface_token:
            logger.error("Web interface token is not configured")
            return None
        try:
            response = requests.post(
                f"{self.base_url}/draft",
                json={"citizen_raw_input": citizen_text},
                headers=self.headers,
                timeout=30,
            )
            if response.status_code == 200:
                return response.json()
            logger.error(
                "Web interface submission rejected with status code: %s",
                response.status_code,
            )
        except requests.RequestException:
            logger.exception("Web interface failed to establish connection with AI Gateway")
        return None
