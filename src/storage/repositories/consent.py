"""Provider-neutral durable consent repository boundary."""
from __future__ import annotations

from typing import Protocol

from core.consent import Consent


class ConsentRepository(Protocol):
    def save(self, consent: Consent) -> None:
        ...

    def get(self, consent_id: str) -> Consent | None:
        ...

    def list_for_subject(self, subject_id: str) -> list[Consent]:
        ...


class InMemoryConsentRepository:
    """Reference repository for tests and local development."""

    def __init__(self) -> None:
        self._items: dict[str, Consent] = {}

    def save(self, consent: Consent) -> None:
        existing = self._items.get(consent.consent_id)
        if existing is not None and existing != consent:
            raise ValueError("Consent identifier already has different content")
        self._items[consent.consent_id] = consent

    def get(self, consent_id: str) -> Consent | None:
        return self._items.get(consent_id)

    def list_for_subject(self, subject_id: str) -> list[Consent]:
        return [
            item for item in self._items.values() if item.subject_id == subject_id
        ]

    def clear(self) -> None:
        """Clear the in-memory test/development repository."""
        self._items.clear()
