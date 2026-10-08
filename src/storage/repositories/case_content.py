"""Provider-neutral boundary for non-durable CivicCase content.

CaseContent is deliberately separate from CivicCase persistence. The canonical
Case repository stores lifecycle/metadata only; an access surface may provide
a transient or device-backed content adapter when content is required.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol


@dataclass(frozen=True)
class CaseContent:
    """Citizen-authored content required for transient Case operations."""

    subject: str
    narrative: str
    claims: tuple[dict[str, object], ...] = field(default_factory=tuple)
    jurisdiction: dict[str, object] = field(default_factory=dict)


class CaseContentRepository(Protocol):
    """Content boundary independent from durable Case persistence."""

    def save(self, case_id: str, content: CaseContent, *, principal_id: str) -> None:
        ...

    def get(self, case_id: str, *, principal_id: str) -> CaseContent | None:
        ...

    def delete(self, case_id: str, *, principal_id: str) -> None:
        ...


class InMemoryCaseContentRepository:
    """Transient content adapter for local development and deterministic tests."""

    def __init__(self) -> None:
        self._content: dict[tuple[str, str], CaseContent] = {}

    def save(self, case_id: str, content: CaseContent, *, principal_id: str) -> None:
        self._content[(principal_id, case_id)] = content

    def get(self, case_id: str, *, principal_id: str) -> CaseContent | None:
        return self._content.get((principal_id, case_id))

    def delete(self, case_id: str, *, principal_id: str) -> None:
        self._content.pop((principal_id, case_id), None)

    def clear(self) -> None:
        self._content.clear()
