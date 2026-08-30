"""Channel-neutral authority discovery capability."""

from dataclasses import dataclass
from typing import List, Protocol

from core.contracts.case import AuthorityReference


@dataclass(frozen=True)
class AuthorityCandidate:
    """A possible authority for a civic case."""

    authority: AuthorityReference
    confidence: float = 0.0
    rationale: str = ""


class AuthorityDiscoveryProvider(Protocol):
    """Provider interface for discovering likely responsible authorities."""

    def discover(
        self,
        *,
        category: str,
        department: str,
        location: str | None = None,
    ) -> List[AuthorityCandidate]:
        ...
