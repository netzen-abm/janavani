"""Canonical authority reference used by civic cases and workflows."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4


@dataclass(frozen=True, slots=True)
class AuthorityReference:
    """Provider-neutral reference to an authority or office.

    This object intentionally records source/provenance metadata without
    claiming that an AI suggestion is an official authority fact.
    """

    authority_id: str = field(default_factory=lambda: str(uuid4()))
    name: str = ""
    jurisdiction: Optional[str] = None
    office_id: Optional[str] = None
    official_source_ref: Optional[str] = None
    source_verified: bool = False
    retrieved_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


__all__ = ["AuthorityReference"]
