"""CSV authority provider kept behind the canonical Authority contract."""
from __future__ import annotations

import csv
import os

from src.core.authority import AuthorityContact, AuthorityRecord


class CsvAuthorityRepository:
    """Compatibility provider for the existing offices.csv dataset."""

    def __init__(self, path: str | None = None) -> None:
        self.path = path or os.getenv("JANAVANI_OFFICES_CSV", "database/offices.csv")

    def get(self, authority_id: str) -> AuthorityRecord | None:
        for record in self._records():
            if record.authority_id == str(authority_id):
                return record
        return None

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
        return [
            record
            for record in self._records()
            if type_query in record.authority_type.lower()
            and city_query in record.jurisdiction.get("city", "").lower()
        ][:limit]

    def _records(self) -> list[AuthorityRecord]:
        try:
            with open(self.path, newline="", encoding="utf-8") as handle:
                rows = csv.DictReader(handle)
                return [self._record(row) for row in rows]
        except (OSError, csv.Error):
            return []

    @staticmethod
    def _record(row: dict[str, str]) -> AuthorityRecord:
        contact = AuthorityContact(
            name=row.get("officer_role", "").strip() or row.get("name", "").strip(),
            address=row.get("address", "").strip(),
            email=row.get("email", "").strip() or None,
            role=row.get("officer_role", "").strip() or None,
            source_ref="database/offices.csv",
            verified=False,
        )
        return AuthorityRecord(
            authority_id=row.get("id", "").strip(),
            name=row.get("name", "").strip(),
            authority_type=row.get("type", "").strip(),
            jurisdiction={"city": row.get("city", "").strip()},
            primary_contact=contact,
            source_refs=("database/offices.csv",),
            verification_status="UNVERIFIED",
        )
