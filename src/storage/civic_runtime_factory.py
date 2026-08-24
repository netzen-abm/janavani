"""Compose the complete civic persistence/service stack."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

from src.core.civic_case_service import CivicCaseService
from src.storage.civic_repository_factory import build_civic_case_repository
from src.storage.repositories.civic_case_events import CivicCaseEventRepository, InMemoryCivicCaseEventRepository
from src.storage.repositories.supabase_civic_case_events import SupabaseCivicCaseEventRepository
from src.storage.repositories.supabase_civic_case_transaction import SupabaseCivicCaseTransaction


@dataclass
class CivicRuntime:
    service: CivicCaseService


def build_civic_runtime(*, supabase_client: Any | None = None) -> CivicRuntime:
    mode = os.getenv("JANAVANI_CIVIC_STORAGE", "memory").lower()
    cases = build_civic_case_repository(supabase_client=supabase_client)

    if mode != "supabase":
        events: CivicCaseEventRepository = InMemoryCivicCaseEventRepository()
        return CivicRuntime(CivicCaseService(cases, events))

    if supabase_client is None:
        raise RuntimeError("Supabase civic storage requires a server-side client")

    events = SupabaseCivicCaseEventRepository(supabase_client)
    transaction = SupabaseCivicCaseTransaction(supabase_client)
    return CivicRuntime(CivicCaseService(cases, events, transaction=transaction))
