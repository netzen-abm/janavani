"""Shared HTTP client mechanics for authenticated Janavani interfaces.

Provider and channel policy remain in the interface adapter. This helper owns
request construction, timeouts and safe error handling only.
"""
from __future__ import annotations

import logging
import os
from typing import Any, Optional

import requests


class JanavaniAgentClient:
    """Call the protected AI-agent API using an interface-specific credential."""

    def __init__(
        self,
        interface_name: str,
        token_env_var: str,
        logger: logging.Logger,
        base_url: Optional[str] = None,
        interface_token: Optional[str] = None,
        http_session: Optional[requests.Session] = None,
    ) -> None:
        configured_url = base_url or os.getenv(
            "JANAVANI_AGENT_BASE_URL", "https://janavani.internal"
        )
        self.base_url = f"{configured_url.rstrip('/')}/api/v1/agent"
        self.interface_name = interface_name
        self.interface_token = interface_token or os.getenv(token_env_var)
        self.logger = logger
        self._session = http_session or requests.Session()
        self.headers = {"Content-Type": "application/json"}
        if self.interface_token:
            self.headers["X-Janavani-Interface-Token"] = self.interface_token

    def request_document_draft(self, citizen_text: str) -> Optional[dict[str, Any]]:
        """Request a draft, returning None for unavailable or rejected calls."""
        if not self.interface_token:
            self.logger.error(
                "%s interface token is not configured", self.interface_name
            )
            return None
        try:
            response = self._session.post(
                f"{self.base_url}/draft",
                json={"citizen_raw_input": citizen_text},
                headers=self.headers,
                timeout=(3, 30),
            )
            response.raise_for_status()
            return response.json()
        except (requests.RequestException, ValueError):
            self.logger.warning(
                "%s draft request failed", self.interface_name, exc_info=True
            )
            return None

    def retrieve_document(self, tracking_id: str) -> Optional[dict[str, Any]]:
        """Retrieve a cached draft only when this interface has credentials."""
        if not self.interface_token:
            self.logger.error(
                "%s interface token is not configured", self.interface_name
            )
            return None
        try:
            response = self._session.get(
                f"{self.base_url}/retrieve/{tracking_id}",
                headers=self.headers,
                timeout=(3, 15),
            )
            response.raise_for_status()
            return response.json()
        except (requests.RequestException, ValueError):
            self.logger.warning(
                "%s document retrieval failed", self.interface_name, exc_info=True
            )
            return None
