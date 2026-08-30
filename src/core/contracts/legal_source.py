"""Canonical contract for verified legal/public sources.

This boundary deliberately separates source retrieval/provenance from legal
reasoning. A missing match is represented explicitly; callers must never treat
absence of a source as permission to invent a legal basis.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class SourceVerificationStatus(str, Enum):
    VERIFIED = "verified"
    PENDING = "pending"
    UNVERIFIED = "unverified"


@dataclass(frozen=True)
class LegalSourceReference:
    source_id: str
    title: str
    citation: str = ""
    url: Optional[str] = None
    jurisdiction: Optional[str] = None
    verification: SourceVerificationStatus = SourceVerificationStatus.UNVERIFIED
    provider: str = ""


@dataclass(frozen=True)
class LegalSourceResult:
    found: bool
    sources: tuple[LegalSourceReference, ...] = ()
    query: str = ""
    message: str = ""

    @classmethod
    def no_verified_source(cls, query: str, message: str = "No verified legal/public source found.") -> "LegalSourceResult":
        return cls(found=False, sources=(), query=query, message=message)

    @classmethod
    def from_sources(cls, query: str, sources: tuple[LegalSourceReference, ...]) -> "LegalSourceResult":
        return cls(found=bool(sources), sources=sources, query=query)
