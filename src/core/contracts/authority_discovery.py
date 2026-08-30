"""Shared contracts for candidate and verified civic authorities."""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class AuthorityStatus(str, Enum):
    CANDIDATE = "candidate"
    VERIFIED = "verified"
    STALE = "stale"


@dataclass(frozen=True)
class AuthorityCandidate:
    authority_id: str
    name: str
    authority_type: str
    jurisdiction: Optional[str]
    reason: str
    source_ids: tuple[str, ...] = ()
    status: AuthorityStatus = AuthorityStatus.CANDIDATE
    to_address: Optional[str] = None
    to_email: Optional[str] = None
    cc_address: Optional[str] = None
    cc_email: Optional[str] = None
