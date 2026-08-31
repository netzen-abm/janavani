"""Canonical gateway for authority discovery.

Legacy discovery providers may remain behind this adapter during migration.
New case, pathway, document and escalation code should consume only the
canonical AuthorityCandidate contract exposed here.
"""
from __future__ import annotations

from typing import Iterable, Protocol

from src.core.capabilities.authority_candidate_adapter import legacy_to_canonical
from src.core.contracts.authority_discovery import AuthorityCandidate, AuthorityStatus


class LegacyDiscoveryProvider(Protocol):
    def discover(self, issue, *, jurisdiction=None, location=None) -> Iterable: ...


class CanonicalAuthorityDiscoveryGateway:
    def __init__(self, legacy_provider: LegacyDiscoveryProvider):
        self.legacy_provider = legacy_provider

    def discover(self, issue, *, jurisdiction=None, location=None) -> tuple[AuthorityCandidate, ...]:
        candidates = self.legacy_provider.discover(issue, jurisdiction=jurisdiction, location=location)
        return tuple(legacy_to_canonical(candidate) for candidate in candidates)

    @staticmethod
    def verified(candidates: Iterable[AuthorityCandidate]) -> tuple[AuthorityCandidate, ...]:
        """Return only candidates with explicit verified status and provenance."""
        return tuple(
            candidate for candidate in candidates
            if candidate.status == AuthorityStatus.VERIFIED and bool(candidate.source_ids)
        )
