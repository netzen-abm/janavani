"""Shared case-law reference capability.

The capability finds potentially relevant Supreme Court/High Court decisions
through an injected provider. It does not invent citations, infer that every
case needs precedent, or provide legal representation.
"""

from __future__ import annotations

from typing import Iterable, Protocol

from src.core.contracts.case_law import CaseLawReference, CaseLawSearchResult


class CaseLawProvider(Protocol):
    def search(self, query: str, *, jurisdiction: str | None = None) -> Iterable[CaseLawReference]: ...


class SharedCaseLawReference:
    def __init__(self, provider: CaseLawProvider):
        self.provider = provider

    def find_relevant(self, query: str, *, jurisdiction: str | None = None) -> CaseLawSearchResult:
        if not query.strip():
            raise ValueError("query is required")
        references = tuple(self.provider.search(query, jurisdiction=jurisdiction))
        return CaseLawSearchResult(query=query, references=references)
