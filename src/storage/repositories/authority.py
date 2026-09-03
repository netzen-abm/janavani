"""Provider-neutral in-memory authority repository."""
from __future__ import annotations

from src.core.authority import AuthorityRecord, AuthorityRepository


class InMemoryAuthorityRepository(AuthorityRepository):
    """Reference implementation for tests and local development."""

    def __init__(self, records: list[AuthorityRecord] | None = None) -> None:
        self._records = {record.authority_id: record for record in records or []}

    def get(self, authority_id: str) -> AuthorityRecord | None:
        return self._records.get(authority_id)

    def save(self, record: AuthorityRecord) -> None:
        self._records[record.authority_id] = record

    def search(
        self,
        *,
        authority_type: str,
        city: str,
        limit: int = 5,
    ) -> list[AuthorityRecord]:
        if limit < 1:
            return []
        type_query = authority_type.strip().lower()
        city_query = city.strip().lower()
        matches = [
            record
            for record in self._records.values()
            if type_query in record.authority_type.lower()
            and city_query in str(record.jurisdiction.get("city", "")).lower()
        ]
        return matches[:limit]
