"""Shared authority database provider boundary.

The existing office database/search implementation can be adapted behind this
interface. No channel gets direct database ownership, and citizen corrections
remain separate from authoritative records until verified.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping, Optional, Protocol

from src.core.capabilities.authority_discovery_service import AuthorityCandidate, AuthorityDiscoveryProvider
from src.core.capabilities.issue_understanding import IssueUnderstanding
from src.core.contracts.case import AuthorityReference, VerificationStatus


@dataclass(frozen=True)
class AuthorityRecord:
    authority_id: str
    name: str
    address: str = ""
    email: Optional[str] = None
    department: Optional[str] = None
    jurisdiction: Optional[str] = None
    verified: bool = True
    source: str = "authority_database"


class AuthorityRepository(Protocol):
    def search(
        self,
        *,
        department: Optional[str] = None,
        jurisdiction: Optional[str] = None,
        location: Optional[str] = None,
        query: Optional[str] = None,
    ) -> Iterable[AuthorityRecord]: ...


class AuthorityDatabaseProvider(AuthorityDiscoveryProvider):
    """Adapt the authoritative office repository to shared discovery."""

    def __init__(self, repository: AuthorityRepository):
        self.repository = repository

    def discover(
        self,
        issue: IssueUnderstanding,
        *,
        jurisdiction: Optional[str] = None,
        location: Optional[str] = None,
    ) -> Iterable[AuthorityCandidate]:
        records = self.repository.search(
            department=issue.department,
            jurisdiction=jurisdiction,
            location=location,
            query=issue.category,
        )
        for record in records:
            yield AuthorityCandidate(
                authority=AuthorityReference(
                    authority_id=record.authority_id,
                    name=record.name,
                    location=record.address,
                    source=record.source,
                    verification=(
                        VerificationStatus.VERIFIED if record.verified else VerificationStatus.PENDING
                    ),
                ),
                confidence=1.0 if record.verified else 0.5,
                rationale="authority database match",
                source=record.source,
            )
