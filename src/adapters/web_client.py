import requests
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("janavani.adapters.web_client")

class JanavaniAIWebClient:
    """Consumes the decoupled Janavani Agentic AI microservice inside the browser interface."""
    def __init__(self, base_url: str = "https://janavani.internal", interface_token: str = "web-mvp-token-abc"):
        self.base_url = f"{base_url}/api/v1/agent"
        self.headers = {
            "X-Janavani-Interface-Token": interface_token,
            "Content-Type": "application/json"
        }

    def request_document_draft(self, citizen_text: str) -> Optional[Dict[str, Any]]:
        """Sends raw citizen issue text to the isolated AI core for processing."""
        url = f"{self.base_url}/draft"
        payload = {"citizen_raw_input": citizen_text}
        
        try:
            response = requests.post(url, json=payload, headers=self.headers, timeout=30)
            if response.status_code == 200:
                return response.json() # Returns tracking_id and structured legal layout variables
            
            logger.error(f"Web interface submission rejected with status code: {response.status_code}")
        except requests.RequestException as connection_error:
            logger.error(f"Web interface failed to establish connection with AI Gateway: {str(connection_error)}")
        return None
