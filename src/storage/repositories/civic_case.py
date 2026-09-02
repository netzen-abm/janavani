"""Provider-neutral persistence boundary for CivicCase."""
from __future__ import annotations

from typing import Protocol

from src.core.civic_case import CivicCase


class CivicCaseRepository(Protocol):
    """Durable or local persistence contract for a CivicCase."""

    def save(self, case: CivicCase) -> None:
        """Persist the current case representation."""
        ...

    def get(self, case_id: str) -> CivicCase | None:
        """Return a case by identifier when present."""
        ...


class InMemoryCivicCaseRepository:
    """Process-local repository used for tests and non-durable development."""

    def __init__(self) -> None:
        self._cases: dict[str, CivicCase] = {}

    def save(self, case: CivicCase) -> None:
        self._cases[case.case_id] = case

    def get(self, case_id: str) -> CivicCase | None:
        return self._cases.get(case_id)

    def clear(self) -> None:
        """Clear local state between tests or development sessions."""
        self._cases.clear()
