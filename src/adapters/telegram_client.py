import requests
import logging
import os
from typing import Dict, Any, Optional

logger = logging.getLogger("janavani.adapters.telegram_client")


class JanavaniAITelegramClient:
    """Connects the existing Telegram bot interface to the isolated AI microservice."""

    def __init__(self, base_url: Optional[str] = None, interface_token: Optional[str] = None):
        configured_base_url = base_url or os.getenv(
            "JANAVANI_AGENT_BASE_URL", "https://janavani.internal"
        )
        self.base_url = f"{configured_base_url.rstrip('/')}/api/v1/agent"
        self.interface_token = interface_token or os.getenv(
            "JANAVANI_TELEGRAM_INTERFACE_TOKEN"
        )
        self.headers = {"Content-Type": "application/json"}
        if self.interface_token:
            self.headers["X-Janavani-Interface-Token"] = self.interface_token

    def request_document_draft(self, citizen_text: str) -> Optional[Dict[str, Any]]:
        """Trigger document drafting for the Telegram bot interface."""
        if not self.interface_token:
            logger.error("Telegram interface token is not configured")
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
                "Telegram client interaction rejected with status code: %s",
                response.status_code,
            )
        except requests.RequestException:
            logger.exception("Telegram client failed to reach AI Gateway")
        return None

    def poll_cached_document(self, tracking_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve an active document template from temporary storage."""
        if not self.interface_token:
            logger.error("Telegram interface token is not configured")
            return None
        try:
            response = requests.get(
                f"{self.base_url}/retrieve/{tracking_id}",
                headers=self.headers,
                timeout=15,
            )
            if response.status_code == 200:
                return response.json()
        except requests.RequestException:
            logger.exception("Telegram client tracking extraction failed")
        return None
