"""Channel-neutral authority resolution contract."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class AuthorityConfidence(str, Enum):
    UNKNOWN = "unknown"
    CANDIDATE = "candidate"
    VERIFIED = "verified"


@dataclass(frozen=True)
class AuthorityCandidate:
    office_id: str
    organisation_id: str | None = None
    confidence: AuthorityConfidence = AuthorityConfidence.UNKNOWN
    source_ref: str | None = None
    rationale: str | None = None


@dataclass(frozen=True)
class AuthorityResolution:
    case_id: str
    candidates: tuple[AuthorityCandidate, ...]
    selected_office_id: str | None = None

    @property
    def verified(self) -> bool:
        return bool(self.selected_office_id) and any(
            c.office_id == self.selected_office_id and c.confidence is AuthorityConfidence.VERIFIED
            for c in self.candidates
        )


def resolve_authority(case_id: str, candidates: list[AuthorityCandidate]) -> AuthorityResolution:
    if not case_id:
        raise ValueError("case_id is required")
    verified = [c for c in candidates if c.confidence is AuthorityConfidence.VERIFIED]
    selected = verified[0].office_id if len(verified) == 1 else None
    return AuthorityResolution(case_id, tuple(candidates), selected)
