"""Provider-neutral contracts shared by every Janavani access surface.

This module intentionally contains interfaces/data contracts only. Concrete
storage, notification, search, AI and channel implementations belong behind
these boundaries.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Protocol


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(frozen=True)
class ProvenanceRef:
    source_id: str
    source_uri: str | None = None
    source_version: str | None = None
    retrieved_at: datetime = field(default_factory=utc_now)
    verification_status: str = "unverified"


@dataclass(frozen=True)
class TrackingEvent:
    event_id: str
    subject_id: str
    event_type: str
    occurred_at: datetime = field(default_factory=utc_now)
    actor_ref: str | None = None
    reference: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class TrackingStore(Protocol):
    def append(self, event: TrackingEvent) -> None: ...

    def list_for(self, subject_id: str) -> list[TrackingEvent]: ...


class ProvenanceStore(Protocol):
    def record(self, subject_id: str, provenance: ProvenanceRef) -> None: ...

    def list_for(self, subject_id: str) -> list[ProvenanceRef]: ...


class NotificationPort(Protocol):
    def notify(self, recipient_ref: str, event: TrackingEvent) -> None: ...
