from src.capabilities.device_security import (
    SecurityEvidence,
    SecurityObservation,
    build_report,
)


def test_heuristic_observation_remains_an_indicator():
    report = build_report(
        [
            SecurityObservation(
                code="WEBDRIVER_PRESENT",
                evidence=SecurityEvidence.INDICATOR,
            )
        ]
    )

    assert report.has_indicators is True
    assert report.has_verified_compromise is False


def test_verified_compromise_requires_explicit_verified_evidence():
    report = build_report(
        [
            SecurityObservation(
                code="COMPROMISE_PLATFORM_ATTESTATION",
                evidence=SecurityEvidence.VERIFIED,
            )
        ]
    )

    assert report.has_verified_compromise is True


def test_unavailable_probe_is_not_compromise():
    report = build_report(
        [
            SecurityObservation(
                code="ROOT_CHECK_UNAVAILABLE",
                evidence=SecurityEvidence.UNAVAILABLE,
            )
        ]
    )

    assert report.has_verified_compromise is False
    assert report.has_indicators is False
