"""Provider-neutral persistence contracts for Janavani domain aggregates."""

from __future__ import annotations

from typing import Any, Mapping, Protocol


class CaseRepository(Protocol):
    def save(self, record: Mapping[str, Any]) -> None:
        """Persist a serialisable canonical case representation."""
        ...

    def get_by_id(self, case_id: str) -> dict[str, Any] | None:
        """Return a case representation or ``None`` when absent."""
        ...


__all__ = ["CaseRepository"]
