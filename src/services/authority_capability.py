"""Governed authority-resolution capability.

Authority selection is kept separate from transport, UI, AI providers and
storage. AI may assist a future implementation, but verified authority data
must remain distinguishable from suggestions.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from src.domain.authority import Authority, AuthorityQuery


class AuthorityProvider(Protocol):
    name: str

    def find(self, query: AuthorityQuery) -> list[Authority]: ...


@dataclass(frozen=True)
class AuthorityMatch:
    authority: Authority
    reason: str
    confidence: float
    verified: bool


class AuthorityCapability:
    """Resolve candidate authorities without inventing official details."""

    def __init__(self, providers: list[AuthorityProvider] | None = None) -> None:
        self._providers = providers or []

    def register(self, provider: AuthorityProvider) -> None:
        self._providers.append(provider)

    def resolve(self, query: AuthorityQuery) -> list[AuthorityMatch]:
        matches: list[AuthorityMatch] = []
        seen: set[str] = set()
        for provider in self._providers:
            for authority in provider.find(query):
                if authority.id in seen:
                    continue
                seen.add(authority.id)
                verified = authority.verification_state == "verified"
                matches.append(
                    AuthorityMatch(
                        authority=authority,
                        reason="provider_match",
                        confidence=1.0 if verified else 0.5,
                        verified=verified,
                    )
                )
        return matches
