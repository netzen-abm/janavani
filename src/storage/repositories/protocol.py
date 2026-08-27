"""Provider-neutral persistence protocols for the Janavani domain.

The domain/application layers depend on these contracts rather than on a
specific database, file format, cache, or hosted provider. Implementations
may be local JSONL, Supabase/PostgreSQL, or another approved adapter.
"""

from __future__ import annotations

from typing import Any, Mapping, Protocol


class CaseRepository(Protocol):
    """Persistence contract for the canonical civic Case aggregate."""

    def save(self, record: Mapping[str, Any]) -> None:
        """Persist a serialisable case representation."""
        ...

    def get_by_id(self, case_id: str) -> dict[str, Any] | None:
        """Return the case representation or ``None`` when absent."""
        ...


__all__ = ["CaseRepository"]
