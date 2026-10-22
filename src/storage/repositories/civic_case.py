"""Provider-neutral persistence boundary for CivicCase."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from src.core.civic_case import CivicCase


@dataclass(frozen=True, slots=True)
class CivicCaseSummary:
    """Metadata-only projection for bounded Case collection views."""

    case_id: str
    case_type: str
    status: str
    created_at: str | None
    updated_at: str | None
    last_activity_at: str | None
    evidence_count: int
    document_count: int


class CivicCaseRepository(Protocol):
    """Durable or local persistence contract for CivicCase."""

    def save(self, case: CivicCase, *, principal_id: str | None = None) -> None:
        """Persist the current case representation."""
        ...

    def get(self, case_id: str, *, principal_id: str | None = None) -> CivicCase | None:
        """Return a case by identifier when present."""
        ...

    def list_for_principal(
        self, principal_id: str, *, limit: int = 20
    ) -> list[CivicCaseSummary]:
        """List metadata-only summaries for Cases owned by a trusted principal."""
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

    def list_for_principal(
        self, principal_id: str, *, limit: int = 20
    ) -> list[CivicCaseSummary]:
        """Build detached summaries without exposing citizen-authored content."""
        if not isinstance(principal_id, str) or not principal_id.strip():
            return []
        bounded_limit = max(1, min(int(limit), 50))
        owned = [case for case in self._cases.values() if case.created_by == principal_id]
        owned.sort(
            key=lambda case: case.updated_at or case.created_at or "",
            reverse=True,
        )
        return [
            CivicCaseSummary(
                case_id=case.case_id,
                case_type=case.case_type.value,
                status=case.status.value,
                created_at=case.created_at,
                updated_at=case.updated_at,
                last_activity_at=(
                    case.events[-1].occurred_at if case.events
                    else case.updated_at or case.created_at
                ),
                evidence_count=len(case.evidence_refs),
                document_count=len(case.document_refs),
            )
            for case in owned[:bounded_limit]
        ]

    def clear(self) -> None:
        """Clear local state between tests or development sessions."""
        self._cases.clear()
