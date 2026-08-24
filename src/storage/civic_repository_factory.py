"""Select the civic repository without exposing storage credentials to clients."""

from __future__ import annotations

import os
from typing import Any

from src.storage.repositories.civic_case_repository import CivicCaseRepository, InMemoryCivicCaseRepository
from src.storage.repositories.supabase_civic_case_repository import SupabaseCivicCaseRepository


def build_civic_case_repository(*, supabase_client: Any | None = None) -> CivicCaseRepository:
    """Use Supabase only when explicitly configured; otherwise stay local/test-safe."""
    if os.getenv("JANAVANI_CIVIC_STORAGE", "memory").lower() != "supabase":
        return InMemoryCivicCaseRepository()
    if supabase_client is None:
        raise RuntimeError("Supabase civic storage requires a server-side client")
    return SupabaseCivicCaseRepository(supabase_client)
