"""Channel-neutral contract for anonymous citizen-owned civic drafts."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class AnonymousCivicDraft:
    """Transient citizen draft, not attached to or persisted as a Janavani Case."""

    document_type: str
    title: str
    subject: str
    body: str
