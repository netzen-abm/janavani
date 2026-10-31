"""Request-scoped transport adapter for citizen-owned saved format API calls."""
from __future__ import annotations

from typing import Any
from urllib.parse import quote

import httpx


class JanavaniDocumentFormatClient:
    """Reuse the verified request-scoped assertion from the canonical API client."""

    def __init__(self, platform_client: Any) -> None:
        self._client = platform_client

    def _request(self, method: str, path: str, *, payload: dict[str, object] | None = None) -> Any:
        headers = self._client._headers()
        response = httpx.request(
            method,
            f"{self._client.base_url}/civic/drafts/formats{path}",
            json=payload,
            headers=headers,
            timeout=20.0,
        )
        response.raise_for_status()
        return response.json() if response.content else {}

    def list_formats(self) -> list[dict[str, object]]:
        return list(self._request("GET", "")["formats"])

    def get_format(self, format_id: str) -> dict[str, object]:
        return self._request("GET", f"/{quote(format_id, safe='')}")

    def save_format(
        self, *, template_id: str, template_version: int,
        section_field_names: list[str], save_confirmation: bool,
    ) -> dict[str, object]:
        return self._request(
            "POST", "",
            payload={
                "template_id": template_id,
                "template_version": template_version,
                "section_field_names": section_field_names,
                "save_confirmation": save_confirmation,
            },
        )

    def delete_format(self, format_id: str, *, delete_confirmation: bool) -> dict[str, object]:
        return self._request(
            "DELETE", f"/{quote(format_id, safe='')}",
            payload={"delete_confirmation": delete_confirmation},
        )
