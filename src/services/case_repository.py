"""Provider-neutral Case repository contract.

Business logic depends on this interface. Storage implementations can be
local, native, test-only, or explicitly approved future providers.
"""
from __future__ import annotations

from typing import Protocol

from src.domain.case import CaseCreate, CaseRecord, CaseStatus


class CaseRepository(Protocol):
    def create(self, payload: CaseCreate) -> CaseRecord: ...
    def get(self, case_id: str) -> CaseRecord | None: ...
    def list(self) -> list[CaseRecord]: ...
    def update_status(self, case_id: str, status: CaseStatus) -> CaseRecord | None: ...
    def delete(self, case_id: str) -> bool: ...


class LocalVaultCaseRepository:
    """Adapter boundary for a client-owned LocalVault.

    The actual browser/native vault is injected by the access surface. This
    class intentionally has no network fallback and no key-management API.
    """

    def __init__(self, vault) -> None:
        self.vault = vault

    def create(self, payload: CaseCreate) -> CaseRecord:
        raise NotImplementedError("client vault adapter implementation is required")

    def get(self, case_id: str) -> CaseRecord | None:
        raise NotImplementedError("client vault adapter implementation is required")

    def list(self) -> list[CaseRecord]:
        raise NotImplementedError("client vault adapter implementation is required")

    def update_status(self, case_id: str, status: CaseStatus) -> CaseRecord | None:
        raise NotImplementedError("client vault adapter implementation is required")

    def delete(self, case_id: str) -> bool:
        raise NotImplementedError("client vault adapter implementation is required")
