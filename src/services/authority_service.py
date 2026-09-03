"""Shared authority lookup facade for all presentation surfaces."""
from __future__ import annotations

from src.core.authority import AuthorityRecord, AuthorityRepository
from src.storage.repositories.authority_csv import CsvAuthorityRepository


def find_authorities(
    department: str,
    location: str,
    *,
    repository: AuthorityRepository | None = None,
    limit: int = 5,
) -> list[AuthorityRecord]:
    """Resolve authorities through the canonical provider-neutral contract."""
    if not department.strip() or not location.strip() or limit < 1:
        return []
    repo = repository or CsvAuthorityRepository()
    return repo.search(
        authority_type=department,
        city=location,
        limit=limit,
    )


def find_authority(
    authority_id: str,
    *,
    repository: AuthorityRepository | None = None,
) -> AuthorityRecord | None:
    """Resolve one authority without exposing its storage provider."""
    if not authority_id.strip():
        return None
    repo = repository or CsvAuthorityRepository()
    return repo.get(authority_id)
