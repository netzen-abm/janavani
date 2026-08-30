"""Shared authority discovery capability.

This service is channel-neutral. It consumes an IssueUnderstanding plus
jurisdiction/context and returns authority candidates with provenance and
verification state. Data supplied directly by a citizen is never promoted to
verified merely because it was supplied.
"""
from dataclasses import dataclass, field
from typing import Iterable, Optional, Protocol

from src.core.contracts.case import AuthorityReference, VerificationStatus
from src.core.capabilities.issue_understanding import IssueUnderstanding


@dataclass(frozen=True)
class AuthorityCandidate:
    authority: AuthorityReference
    confidence: float = 0.0
    rationale: str = ""
    source: str = "system"


class AuthorityDiscoveryProvider(Protocol):
    def discover(
        self,
        issue: IssueUnderstanding,
        *,
        jurisdiction: Optional[str] = None,
        location: Optional[str] = None,
    ) -> Iterable[AuthorityCandidate]: ...


class SharedAuthorityDiscovery:
    def __init__(self, provider: AuthorityDiscoveryProvider):
        self.provider = provider

    def discover(
        self,
        issue: IssueUnderstanding,
        *,
        jurisdiction: Optional[str] = None,
        location: Optional[str] = None,
    ) -> list[AuthorityCandidate]:
        candidates = list(self.provider.discover(issue, jurisdiction=jurisdiction, location=location))
        return [self._normalize(candidate) for candidate in candidates]

    @staticmethod
    def _normalize(candidate: AuthorityCandidate) -> AuthorityCandidate:
        authority = candidate.authority
        if authority.source == "citizen_provided" and authority.verification == VerificationStatus.UNKNOWN:
            authority = AuthorityReference(
                authority_id=authority.authority_id,
                name=authority.name,
                location=authority.location,
                source=authority.source,
                verification=VerificationStatus.PENDING,
            )
        return AuthorityCandidate(
            authority=authority,
            confidence=max(0.0, min(1.0, candidate.confidence)),
            rationale=candidate.rationale,
            source=candidate.source,
        )
