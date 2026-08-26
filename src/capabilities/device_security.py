"""Truthful device-security capability boundary.

This module deliberately contains no platform-specific probing. Platform adapters
may supply observations later; this domain model prevents heuristic observations
from being represented as proof of compromise.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Iterable


class SecurityEvidence(str, Enum):
    VERIFIED = "VERIFIED"
    INDICATOR = "INDICATOR"
    UNKNOWN = "UNKNOWN"
    UNAVAILABLE = "UNAVAILABLE"


@dataclass(frozen=True)
class SecurityObservation:
    code: str
    evidence: SecurityEvidence
    detail: str = ""


@dataclass(frozen=True)
class DeviceSecurityReport:
    observations: tuple[SecurityObservation, ...] = field(default_factory=tuple)

    @property
    def has_verified_compromise(self) -> bool:
        return any(
            observation.evidence is SecurityEvidence.VERIFIED
            and observation.code.startswith("COMPROMISE_")
            for observation in self.observations
        )

    @property
    def has_indicators(self) -> bool:
        return any(
            observation.evidence is SecurityEvidence.INDICATOR
            for observation in self.observations
        )


def build_report(observations: Iterable[SecurityObservation]) -> DeviceSecurityReport:
    """Build a platform-neutral report without upgrading evidence strength."""
    return DeviceSecurityReport(tuple(observations))
