"""Web adapter for the authenticated identity-pairing lifecycle."""
from __future__ import annotations

from typing import Any
from urllib.parse import quote

import httpx

from src.webapp.services.api_client import authorization_headers


class IdentityPairingAPIClient:
    """Call the canonical pairing API using the current citizen's assertion."""

    def __init__(self, *, base_url: str, identity_assertion: str | None) -> None:
        self.base_url = base_url.rstrip("/")
        self.identity_assertion = identity_assertion

    def issue(self) -> dict[str, Any]:
        response = httpx.post(
            f"{self.base_url}/civic/identity-pairings",
            headers=authorization_headers(self.identity_assertion),
            timeout=15.0,
        )
        response.raise_for_status()
        return response.json()

    def confirm(self, pairing_id: str) -> dict[str, Any]:
        if not pairing_id.strip():
            raise ValueError("Pairing reference is required")
        response = httpx.post(
            f"{self.base_url}/civic/identity-pairings/{quote(pairing_id, safe='')}/confirm",
            json={"explicit_confirmation": True},
            headers=authorization_headers(self.identity_assertion),
            timeout=15.0,
        )
        response.raise_for_status()
        return response.json()
