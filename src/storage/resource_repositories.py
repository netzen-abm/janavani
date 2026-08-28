"""Supabase repositories for canonical resource records.

Relationship linking and append-only event persistence remain in
``relationship_repository`` so these repositories have one responsibility:
CRUD for their resource table.
"""

from __future__ import annotations

from typing import Any, Callable, TypeVar

from src.domain.authority import Authority
from src.domain.document import Document
from src.domain.evidence import Evidence
from src.storage.hydration import authority_from_row, document_from_row, evidence_from_row
from src.storage.serialization import authority_row, document_row, evidence_row

T = TypeVar("T")


class SupabaseResourceRepository:
    def __init__(self, client: Any) -> None:
        if client is None:
            raise ValueError("Supabase client is required")
        self.client = client

    def _get(self, table: str, key: str, value: str, hydrate: Callable[[dict[str, Any]], T]) -> T | None:
        response = self.client.table(table).select("*").eq(key, value).limit(1).execute()
        rows = getattr(response, "data", None) or []
        return hydrate(rows[0]) if rows else None

    def _save(self, table: str, row: dict[str, Any], hydrate: Callable[[dict[str, Any]], T]) -> T:
        response = self.client.table(table).upsert(row).execute()
        rows = getattr(response, "data", None) or []
        return hydrate(rows[0]) if rows else hydrate(row)


class SupabaseEvidenceRepository(SupabaseResourceRepository):
    table_name = "evidence"

    def get(self, evidence_id: str) -> Evidence | None:
        return self._get(self.table_name, "evidence_id", evidence_id, evidence_from_row)

    def save(self, evidence: Evidence) -> Evidence:
        return self._save(self.table_name, evidence_row(evidence), evidence_from_row)


class SupabaseAuthorityRepository(SupabaseResourceRepository):
    table_name = "authorities"

    def get(self, authority_id: str) -> Authority | None:
        return self._get(self.table_name, "authority_id", authority_id, authority_from_row)

    def save(self, authority: Authority) -> Authority:
        return self._save(self.table_name, authority_row(authority), authority_from_row)


class SupabaseDocumentRepository(SupabaseResourceRepository):
    table_name = "documents"

    def get(self, document_id: str) -> Document | None:
        return self._get(self.table_name, "document_id", document_id, document_from_row)

    def save(self, document: Document) -> Document:
        return self._save(self.table_name, document_row(document), document_from_row)
