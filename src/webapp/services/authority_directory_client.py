"""Web adapter for searching the canonical verified-authority directory."""
from __future__ import annotations

from typing import Any

import httpx

from src.webapp.api_errors import PlatformAPIContractError
from src.webapp.services.api_client import authorization_headers


class AuthorityDirectoryAPIClient:
    """Request-scoped client for the shared Authority capability API."""

    def __init__(self, *, base_url: str, identity_assertion: str | None) -> None:
        self.base_url = base_url.rstrip("/")
        self.identity_assertion = identity_assertion

    def search(self, *, authority_type: str, city: str, limit: int = 10) -> list[dict[str, Any]]:
        response = httpx.get(
            f"{self.base_url}/civic/authorities/search",
            params={
                "authority_type": authority_type,
                "city": city,
                "limit": max(1, min(limit, 20)),
            },
            headers=authorization_headers(self.identity_assertion),
            timeout=15.0,
        )
        response.raise_for_status()
        payload = response.json()
        if not isinstance(payload, dict) or not isinstance(payload.get("items"), list):
            raise PlatformAPIContractError("Authority API returned an invalid search response")
        items = []
        for item in payload["items"]:
            if not isinstance(item, dict):
                raise PlatformAPIContractError("Authority API returned an invalid directory entry")
            if item.get("verified") is not True:
                continue
            if not all(isinstance(item.get(key), str) and item[key].strip()
                       for key in ("authority_id", "name", "authority_type")):
                raise PlatformAPIContractError("Verified authority entry is incomplete")
            items.append(item)
        return items
