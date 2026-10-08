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

    def clear(self) -> None:
        """Clear local state between tests or development sessions."""
        self._cases.clear()
