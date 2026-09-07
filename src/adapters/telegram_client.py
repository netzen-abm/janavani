"""Provider-neutral Telegram adapter for the optional AI capability."""
from __future__ import annotations

import logging
import os
from typing import Any, Dict, Optional

import requests

logger = logging.getLogger("janavani.adapters.telegram_client")


class JanavaniAITelegramClient:
    """Connect Telegram to an independently deployed AI capability."""

    def __init__(
        self,
        base_url: str | None = None,
        interface_token: str | None = None,
    ):
        resolved_base_url = (
            base_url
            or os.getenv("JANAVANI_AI_BASE_URL")
            or os.getenv("JANAVANI_INTERNAL_API_URL")
            or "http://localhost:8000"
        )
        resolved_token = interface_token or os.getenv("JANAVANI_INTERFACE_TOKENS")
        if not resolved_token:
            raise ValueError(
                "JANAVANI_INTERFACE_TOKENS is required for the Telegram AI adapter"
            )

        # A comma-separated interface-token variable is supported by the
        # shared gateway contract. The first token is used by this adapter;
        # production deployments should provide a dedicated service token.
        token = resolved_token.split(",", 1)[0].strip()
        if not token:
            raise ValueError("JANAVANI_INTERFACE_TOKENS contains no usable token")

        self.base_url = f"{resolved_base_url.rstrip('/')}/api/v1/agent"
        self.headers = {
            "X-Janavani-Interface-Token": token,
            "Content-Type": "application/json",
        }

    def request_document_draft(self, citizen_text: str) -> Optional[Dict[str, Any]]:
        """Request optional AI-assisted document drafting."""
        url = f"{self.base_url}/draft"
        payload = {"citizen_raw_input": citizen_text}

        try:
            response = requests.post(url, json=payload, headers=self.headers, timeout=30)
            if response.status_code == 200:
                return response.json()
            logger.error(
                "Telegram AI request rejected with status code: %s",
                response.status_code,
            )
        except requests.RequestException as connection_error:
            logger.error(
                "Telegram AI adapter failed to reach capability service: %s",
                connection_error,
            )
        return None

    def poll_cached_document(self, tracking_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve an AI-generated document from the independent capability service."""
        url = f"{self.base_url}/retrieve/{tracking_id}"

        try:
            response = requests.get(url, headers=self.headers, timeout=15)
            if response.status_code == 200:
                return response.json()
        except requests.RequestException as tracking_error:
            logger.error(
                "Telegram AI tracking request failed: %s",
                tracking_error,
            )
        return None
