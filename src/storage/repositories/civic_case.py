"""Provider-neutral persistence boundary for CivicCase."""
from __future__ import annotations

from copy import deepcopy
from threading import RLock
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
    """Process-local repository with serialized, optimistic Case writes."""

    def __init__(self, store: dict[str, CivicCase] | None = None) -> None:
        self._cases = store if store is not None else {}
        self._lock = RLock()
        # Development/test composition keeps transient citizen content beside,
        # but not inside, the durable Case map. Production providers inject the
        # content boundary explicitly.
        from src.storage.repositories.case_content import InMemoryCaseContentRepository
        self.content_repository = InMemoryCaseContentRepository()

    def save(self, case: CivicCase, *, principal_id: str | None = None) -> None:
        with self._lock:
            current = self._cases.get(case.case_id)
            if current is not None and case.version != current.version:
                raise RuntimeError(
                    f"Expected Case version {case.version}, found {current.version}"
                )
            stored = deepcopy(case)
            stored.version = current.version + 1 if current is not None else max(1, case.version)
            stored.subject = stored.case_type.value
            stored.narrative = ""
            self._cases[case.case_id] = stored
            case.version = stored.version

    def get(self, case_id: str, *, principal_id: str | None = None) -> CivicCase | None:
        with self._lock:
            case = self._cases.get(case_id)
            return deepcopy(case) if case is not None else None

    def clear(self) -> None:
        """Clear local state between tests or development sessions."""
        with self._lock:
            self._cases.clear()
