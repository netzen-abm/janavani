"""Supabase implementation of the shared storage boundary."""

from __future__ import annotations

from typing import Any, Mapping

from supabase import Client, create_client

from src.core.config import Config
from src.platform.storage import StorageResult


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

    def get(self, collection: str, key: str) -> StorageResult:
        try:
            response = self._client.table(collection).select("*").eq("id", key).limit(1).execute()
            rows = response.data or []
            return StorageResult(ok=True, value=rows[0] if rows else None)
        except Exception as exc:
            return StorageResult(ok=False, error_code=type(exc).__name__)

    def put(self, collection: str, key: str, value: Any) -> StorageResult:
        try:
            payload = dict(value) if isinstance(value, Mapping) else {"value": value}
            payload["id"] = key
            response = self._client.table(collection).upsert(payload).execute()
            rows = response.data or []
            return StorageResult(ok=True, value=rows[0] if rows else payload)
        except Exception as exc:
            return StorageResult(ok=False, error_code=type(exc).__name__)

    def delete(self, collection: str, key: str) -> StorageResult:
        try:
            response = self._client.table(collection).delete().eq("id", key).execute()
            return StorageResult(ok=True, value=response.data or [])
        except Exception as exc:
            return StorageResult(ok=False, error_code=type(exc).__name__)

    def health(self) -> Mapping[str, Any]:
        """Report adapter configuration without performing a database query."""
        return {"provider": self.name, "configured": True}
