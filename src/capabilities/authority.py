"""Channel-neutral Authority Discovery capability contract."""

from dataclasses import dataclass
from typing import Protocol, Sequence


@dataclass(frozen=True)
class AuthorityCandidate:
    authority_id: str
    name: str
    authority_type: str | None = None
    jurisdiction: str | None = None
    source: str | None = None
    source_url: str | None = None
    retrieved_at: str | None = None
    confidence: float | None = None


class AuthorityCapability(Protocol):
    def discover(self, *, query: str, jurisdiction: str | None = None) -> Sequence[AuthorityCandidate]: ...
