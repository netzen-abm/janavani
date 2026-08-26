import requests
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("janavani.adapters.telegram_client")

class JanavaniAITelegramClient:
    """Connects the existing Telegram bot interface to the isolated AI microservice."""
    def __init__(self, base_url: str = "https://janavani.internal", interface_token: str = "telegram-mvp-token-xyz"):
        self.base_url = f"{base_url}/api/v1/agent"
        self.headers = {
            "X-Janavani-Interface-Token": interface_token,
            "Content-Type": "application/json"
        }

    def request_document_draft(self, citizen_text: str) -> Optional[Dict[str, Any]]:
        """Triggers document drafting for the Telegram bot interface."""
        url = f"{self.base_url}/draft"
        payload = {"citizen_raw_input": citizen_text}
        
        try:
            response = requests.post(url, json=payload, headers=self.headers, timeout=30)
            if response.status_code == 200:
                return response.json()
            
            logger.error(f"Telegram client interaction rejected with status code: {response.status_code}")
        except requests.RequestException as connection_error:
            logger.error(f"Telegram client failed to reach AI Gateway: {str(connection_error)}")
        return None

    def poll_cached_document(self, tracking_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves an active document template block from temporary storage before it expires."""
        url = f"{self.base_url}/retrieve/{tracking_id}"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=15)
            if response.status_code == 200:
                return response.json()
        except requests.RequestException as tracking_error:
            logger.error(f"Telegram client tracking extraction dropped: {str(tracking_error)}")
        return None
