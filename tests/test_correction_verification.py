import pytest

from src.core.capabilities.correction_verification import (
    SharedCorrectionVerification,
    VerificationEvidence,
    VerificationOutcome,
)


def test_new_correction_is_pending():
    record = SharedCorrectionVerification().submit_for_verification("corr-1")
    assert record.outcome == VerificationOutcome.PENDING


def test_verification_requires_independent_evidence():
    with pytest.raises(ValueError):
        SharedCorrectionVerification().verify("corr-1", ())


def test_correction_can_be_verified_with_source_evidence():
    evidence = (VerificationEvidence("official_registry", "office-123", "2026-08-30"),)
    record = SharedCorrectionVerification().verify("corr-1", evidence, verifier="authority-check")
    assert record.outcome == VerificationOutcome.VERIFIED
    assert record.evidence[0].source_ref == "office-123"


def test_correction_can_be_rejected():
    record = SharedCorrectionVerification().reject("corr-1", note="source did not confirm address")
    assert record.outcome == VerificationOutcome.REJECTED
