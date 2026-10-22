"""Provider-neutral persistence boundary for CivicCase."""
from __future__ import annotations

from typing import Protocol

from src.core.civic_case import CivicCase


class CivicCaseRepository(Protocol):
    """Durable or local persistence contract for CivicCase."""

    def save(self, case: CivicCase, *, principal_id: str | None = None) -> None:
        """Persist the current case representation."""
        ...

    def get(self, case_id: str, *, principal_id: str | None = None) -> CivicCase | None:
        """Return a case by identifier when present."""
        ...

    def list_for_principal(self, principal_id: str, *, limit: int = 20) -> list[CivicCase]:
        """List only Cases owned by the supplied trusted principal."""
        ...


class InMemoryCivicCaseRepository:
    """Process-local repository used for tests and development."""

    def __init__(self, store: dict[str, CivicCase] | None = None) -> None:
        self._cases = store if store is not None else {}
        # Development/test composition keeps transient citizen content beside,
        # but not inside, the durable Case map. Production providers inject the
        # content boundary explicitly.
        from src.storage.repositories.case_content import InMemoryCaseContentRepository
        self.content_repository = InMemoryCaseContentRepository()

    def save(self, case: CivicCase, *, principal_id: str | None = None) -> None:
        from copy import deepcopy
        stored = deepcopy(case)
        stored.subject = stored.case_type.value
        stored.narrative = ""
        self._cases[case.case_id] = stored

    def get(self, case_id: str, *, principal_id: str | None = None) -> CivicCase | None:
        return self._cases.get(case_id)

    def list_for_principal(self, principal_id: str, *, limit: int = 20) -> list[CivicCase]:
        """Return detached metadata-only Cases for one owner; blank identity fails closed."""
        if not isinstance(principal_id, str) or not principal_id.strip():
            return []
        from copy import deepcopy
        bounded_limit = max(1, min(int(limit), 50))
        owned = [case for case in self._cases.values() if case.created_by == principal_id]
        owned.sort(
            key=lambda case: case.events[-1].occurred_at if case.events
            else (case.updated_at or case.created_at or ""),
            reverse=True,
        )
        metadata = deepcopy(owned[:bounded_limit])
        for case in metadata:
            # The in-memory repository can share objects with owner-scoped reads;
            # explicitly strip transient citizen-authored fields from this list result.
            case.subject = case.case_type.value
            case.narrative = ""
            case.claims = []
            case.jurisdiction = {}
            for event in case.events:
                event.notes = None
        return metadata

    def clear(self) -> None:
        """Clear local state between tests or development sessions."""
        self._cases.clear()
