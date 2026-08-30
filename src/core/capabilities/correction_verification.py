"""Shared verification lifecycle for citizen corrections.

A correction is an observation/proposal until independently verified. This
module intentionally does not decide truth from user agreement alone.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class VerificationOutcome(str, Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"


@dataclass(frozen=True)
class VerificationEvidence:
    source_type: str
    source_ref: str
    checked_at: str
    note: Optional[str] = None


@dataclass(frozen=True)
class CorrectionVerificationRecord:
    correction_id: str
    outcome: VerificationOutcome
    evidence: tuple[VerificationEvidence, ...] = ()
    verifier: str = "system"
    note: Optional[str] = None


class SharedCorrectionVerification:
    """Verify corrections through explicit evidence rather than trust-by-default."""

    def submit_for_verification(self, correction_id: str) -> CorrectionVerificationRecord:
        if not correction_id.strip():
            raise ValueError("correction_id is required")
        return CorrectionVerificationRecord(correction_id, VerificationOutcome.PENDING)

    def verify(
        self,
        correction_id: str,
        evidence: tuple[VerificationEvidence, ...],
        *,
        verifier: str = "system",
        note: Optional[str] = None,
    ) -> CorrectionVerificationRecord:
        if not correction_id.strip():
            raise ValueError("correction_id is required")
        if not evidence:
            raise ValueError("independent verification evidence is required")
        if not all(item.source_ref.strip() and item.source_type.strip() for item in evidence):
            raise ValueError("verification evidence must identify its source")
        return CorrectionVerificationRecord(
            correction_id=correction_id,
            outcome=VerificationOutcome.VERIFIED,
            evidence=evidence,
            verifier=verifier,
            note=note,
        )

    def reject(
        self,
        correction_id: str,
        *,
        verifier: str = "system",
        note: Optional[str] = None,
    ) -> CorrectionVerificationRecord:
        if not correction_id.strip():
            raise ValueError("correction_id is required")
        return CorrectionVerificationRecord(
            correction_id=correction_id,
            outcome=VerificationOutcome.REJECTED,
            verifier=verifier,
            note=note,
        )
