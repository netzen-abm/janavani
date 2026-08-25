"""Supabase implementation of the shared storage boundary.

This adapter is intentionally small: provider-specific client construction
stays here while callers depend on ``StorageAdapter`` from ``src.platform``.
"""

from __future__ import annotations

from typing import Any, Mapping

from supabase import Client, create_client

from src.core.config import Config


class SupabaseStorageAdapter:
    """Provider adapter for Janavani's current Supabase deployment."""

    name = "supabase"

    def __init__(self, client: Client) -> None:
        self._client = client

    @classmethod
    def from_config(cls) -> "SupabaseStorageAdapter | None":
        url = Config.SUPABASE_URL
        key = Config.SUPABASE_ANON_KEY
        if not url or not key:
            return None
        return cls(create_client(url, key))

    @property
    def client(self) -> Client:
        """Expose the provider client only to provider-specific code."""
        return self._client

    def health(self) -> Mapping[str, Any]:
        """Report adapter configuration without performing a database query."""
        return {"provider": self.name, "configured": True}
