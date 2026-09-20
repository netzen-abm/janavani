"""Provider-neutral atomic boundary for submission consent + Case state.

The capability layer owns authorization and domain validation. This contract
owns only the persistence invariant: consent and the resulting Case projection
must commit or roll back together.
"""
from __future__ import annotations

from typing import Protocol

from src.core.consent import Consent
from src.core.civic_case import CivicCase


class ConsentCaseAtomicRepository(Protocol):
    def save_consent_and_case(
        self,
        consent: Consent,
        case: CivicCase,
        *,
        principal_id: str,
    ) -> None:
        """Atomically persist consent and its Case projection."""
        ...
