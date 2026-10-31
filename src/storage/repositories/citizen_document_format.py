"""Repository contract and isolated in-memory test provider for saved formats."""
from __future__ import annotations

from threading import RLock
from typing import Protocol

from src.documents.citizen_document_format import CitizenDocumentFormat


class CitizenDocumentFormatRepository(Protocol):
    def save(self, record: CitizenDocumentFormat, *, owner_principal_id: str) -> CitizenDocumentFormat: ...
    def list_for_owner(self, *, owner_principal_id: str) -> list[CitizenDocumentFormat]: ...
    def get_for_owner(self, format_id: str, *, owner_principal_id: str) -> CitizenDocumentFormat | None: ...
    def delete_for_owner(self, format_id: str, *, owner_principal_id: str) -> bool: ...


class InMemoryCitizenDocumentFormatRepository:
    """Process-local reference provider for tests only; not restart-safe."""

    def __init__(self) -> None:
        self._records: dict[str, CitizenDocumentFormat] = {}
        self._by_owner_hash: dict[tuple[str, str], str] = {}
        self._lock = RLock()

    def save(self, record: CitizenDocumentFormat, *, owner_principal_id: str) -> CitizenDocumentFormat:
        if owner_principal_id != record.owner_principal_id:
            raise PermissionError("Format owner does not match authenticated principal")
        with self._lock:
            existing_id = self._by_owner_hash.get((owner_principal_id, record.structure_hash))
            if existing_id:
                return self._records[existing_id]
            self._records[record.format_id] = record
            self._by_owner_hash[(owner_principal_id, record.structure_hash)] = record.format_id
            return record

    def list_for_owner(self, *, owner_principal_id: str) -> list[CitizenDocumentFormat]:
        with self._lock:
            records = (item for item in self._records.values() if item.owner_principal_id == owner_principal_id)
            return sorted(records, key=lambda item: (item.created_at, item.format_id))

    def get_for_owner(self, format_id: str, *, owner_principal_id: str) -> CitizenDocumentFormat | None:
        with self._lock:
            record = self._records.get(format_id)
            if record is None or record.owner_principal_id != owner_principal_id:
                return None
            return record

    def delete_for_owner(self, format_id: str, *, owner_principal_id: str) -> bool:
        with self._lock:
            record = self._records.get(format_id)
            if record is None or record.owner_principal_id != owner_principal_id:
                return False
            self._records.pop(format_id, None)
            self._by_owner_hash.pop((owner_principal_id, record.structure_hash), None)
            return True
