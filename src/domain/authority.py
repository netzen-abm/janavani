"""Canonical authority intelligence contract."""
from __future__ import annotations
from datetime import datetime
from pydantic import BaseModel, Field


class VerificationState:
    UNVERIFIED = "unverified"
    VERIFIED = "verified"
    STALE = "stale"


class Authority(BaseModel):
    id: str
    name: str = Field(min_length=2, max_length=300)
    department: str | None = None
    jurisdiction: str | None = None
    address: str | None = None
    contact: str | None = None
    source_url: str | None = None
    verification_state: str = VerificationState.UNVERIFIED
    verified_at: datetime | None = None


class AuthorityQuery(BaseModel):
    issue: str = Field(min_length=3, max_length=10000)
    location: str | None = Field(default=None, max_length=500)


class AuthorityRepository:
    def find(self, query: AuthorityQuery) -> list[Authority]:  # pragma: no cover
        raise NotImplementedError


class InMemoryAuthorityRepository(AuthorityRepository):
    def __init__(self, authorities: list[Authority] | None = None) -> None:
        self._authorities = authorities or []

    def find(self, query: AuthorityQuery) -> list[Authority]:
        terms = set(query.issue.lower().split())
        location = (query.location or "").lower()
        matches = []
        for authority in self._authorities:
            haystack = " ".join(filter(None, [authority.name, authority.department, authority.jurisdiction])).lower()
            if terms.intersection(haystack.split()) or (location and location in haystack):
                matches.append(authority)
        return matches
