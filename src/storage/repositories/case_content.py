"""Provider-neutral boundary for non-durable CivicCase content.

CaseContent is deliberately separate from CivicCase persistence. The canonical
Case repository stores lifecycle/metadata only; a surface may provide transient
or device-backed content when needed. This module never persists citizen content.
"""
from __future__ import annotations

from collections import OrderedDict
from dataclasses import dataclass, field
from threading import RLock
from time import monotonic
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


def _copy_content(content: CaseContent) -> CaseContent:
    return CaseContent(
        subject=content.subject,
        narrative=content.narrative,
        claims=tuple(dict(claim) for claim in content.claims),
        jurisdiction=dict(content.jurisdiction),
    )


class InMemoryCaseContentRepository:
    """Non-expiring in-memory adapter for local development and deterministic tests."""

    def __init__(self) -> None:
        self._content: dict[tuple[str, str], CaseContent] = {}

    def save(self, case_id: str, content: CaseContent, *, principal_id: str) -> None:
        self._content[(principal_id, case_id)] = _copy_content(content)

    def get(self, case_id: str, *, principal_id: str) -> CaseContent | None:
        content = self._content.get((principal_id, case_id))
        return _copy_content(content) if content is not None else None

    def delete(self, case_id: str, *, principal_id: str) -> None:
        self._content.pop((principal_id, case_id), None)

    def clear(self) -> None:
        self._content.clear()


class TransientCaseContentRepository:
    """Bounded, TTL-expiring content adapter; never a durable source of record."""

    def __init__(self, *, ttl_seconds: int = 900, max_entries: int = 1000) -> None:
        if ttl_seconds < 1 or max_entries < 1:
            raise ValueError("Transient content TTL and capacity must be positive")
        self._ttl_seconds = ttl_seconds
        self._max_entries = max_entries
        self._content: OrderedDict[
            tuple[str, str], tuple[CaseContent, float]
        ] = OrderedDict()
        self._lock = RLock()

    def _purge_expired(self, now: float) -> None:
        expired = [
            key for key, (_, expires_at) in self._content.items()
            if expires_at <= now
        ]
        for key in expired:
            self._content.pop(key, None)

    def save(self, case_id: str, content: CaseContent, *, principal_id: str) -> None:
        key = (principal_id, case_id)
        now = monotonic()
        with self._lock:
            self._purge_expired(now)
            self._content[key] = (_copy_content(content), now + self._ttl_seconds)
            self._content.move_to_end(key)
            while len(self._content) > self._max_entries:
                self._content.popitem(last=False)

    def get(self, case_id: str, *, principal_id: str) -> CaseContent | None:
        now = monotonic()
        key = (principal_id, case_id)
        with self._lock:
            self._purge_expired(now)
            entry = self._content.get(key)
            return _copy_content(entry[0]) if entry is not None else None

    def delete(self, case_id: str, *, principal_id: str) -> None:
        with self._lock:
            self._content.pop((principal_id, case_id), None)

    def clear(self) -> None:
        with self._lock:
            self._content.clear()
