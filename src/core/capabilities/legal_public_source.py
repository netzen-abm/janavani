"""Shared legal/public-source provider boundary."""

from __future__ import annotations

from typing import Iterable, Protocol

from src.core.contracts.legal_source import LegalSourceReference, LegalSourceResult


class LegalSourceProvider(Protocol):
    def search(self, query: str, *, jurisdiction: str | None = None) -> Iterable[LegalSourceReference]: ...


class LegalPublicSourceCapability:
    """Expose verified source retrieval to every access surface.

    The provider supplies evidence; it does not assert a legal conclusion.
    """

    def __init__(self, provider: LegalSourceProvider):
        self.provider = provider

    def find(self, query: str, *, jurisdiction: str | None = None) -> LegalSourceResult:
        sources = tuple(
            source
            for source in self.provider.search(query, jurisdiction=jurisdiction)
            if source.verification.value == "verified"
        )
        if not sources:
            return LegalSourceResult.no_verified_source(query)
        return LegalSourceResult.from_sources(query, sources)
