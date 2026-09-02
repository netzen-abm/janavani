"""Provider-neutral persistence boundary for CivicCase."""
from __future__ import annotations

from typing import Protocol

from src.core.civic_case import CivicCase


class CivicCaseRepository(Protocol):
    """Durable or local persistence contract for CivicCase."""

    def save(self, case: CivicCase) -> None:
        """Persist the current case representation."""
        ...

    def get(self, case_id: str) -> CivicCase | None:
        """Return a case by identifier when present."""
        ...


class InMemoryCivicCaseRepository:
    """Process-local repository used for tests and development."""

    def __init__(self, store: dict[str, CivicCase] | None = None) -> None:
        self._cases = store if store is not None else {}

    def save(self, case: CivicCase) -> None:
        self._cases[case.case_id] = case

    def get(self, case_id: str) -> CivicCase | None:
        return self._cases.get(case_id)

    def clear(self) -> None:
        """Clear local state between tests or development sessions."""
        self._cases.clear()
