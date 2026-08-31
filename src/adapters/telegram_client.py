import logging
from typing import Any, Dict, Optional

import requests

from src.core.interface_credentials import get_interface_credential

logger = logging.getLogger("janavani.adapters.telegram_client")


class JanavaniAITelegramClient:
    """Connect the Telegram interface to the isolated AI microservice."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        interface_token: Optional[str] = None,
    ):
        self.base_url = (base_url or "https://janavani.internal").rstrip("/") + "/api/v1/agent"
        token = interface_token or get_interface_credential("JANAVANI_TELEGRAM_INTERFACE_TOKEN").value
        self.headers = {
            "X-Janavani-Interface-Token": token,
            "Content-Type": "application/json",
        }

    def request_document_draft(self, citizen_text: str) -> Optional[Dict[str, Any]]:
        """Trigger document drafting for the Telegram interface."""
        try:
            response = requests.post(
                f"{self.base_url}/draft",
                json={"citizen_raw_input": citizen_text},
                headers=self.headers,
                timeout=30,
            )
            if response.status_code == 200:
                return response.json()
            logger.error("Telegram submission rejected: status=%s", response.status_code)
        except requests.RequestException as exc:
            logger.error("Telegram client failed to reach AI Gateway: %s", exc)
        return None

    def poll_cached_document(self, tracking_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a temporary document block by tracking ID."""
        try:
            response = requests.get(
                f"{self.base_url}/retrieve/{tracking_id}",
                headers=self.headers,
                timeout=15,
            )
            if response.status_code == 200:
                return response.json()
        except requests.RequestException as exc:
            logger.error("Telegram tracking retrieval failed: %s", exc)
        return None
