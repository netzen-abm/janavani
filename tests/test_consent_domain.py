from datetime import datetime, timezone

from src.core.consent import Consent, ConsentGrantType, ConsentStatus


def _consent(*, status=ConsentStatus.GRANTED, expires_at=None):
    return Consent(
        consent_id="consent-1",
        subject_id="citizen-1",
        purpose="case_submission",
        scope=("office:office-1",),
        grant_type=ConsentGrantType.EXPLICIT,
        status=status,
        created_at="2026-09-20T00:00:00+00:00",
        expires_at=expires_at,
        revoked_at="2026-09-20T01:00:00+00:00" if status is ConsentStatus.REVOKED else None,
    )


def test_granted_consent_without_expiry_authorizes_matching_purpose_and_scope():
    assert _consent().authorizes("case_submission", "office:office-1")


def test_expired_consent_does_not_authorize():
    consent = _consent(expires_at="2026-09-20T01:00:00+00:00")
    now = datetime(2026, 9, 20, 2, 0, tzinfo=timezone.utc)
    assert not consent.is_authorized_at(now)
    assert not consent.authorizes("case_submission", "office:office-1", now=now)


def test_consent_expires_at_boundary():
    consent = _consent(expires_at="2026-09-20T01:00:00+00:00")
    now = datetime(2026, 9, 20, 1, 0, tzinfo=timezone.utc)
    assert not consent.is_authorized_at(now)


def test_malformed_expiry_fails_closed():
    consent = _consent(expires_at="not-a-timestamp")
    assert not consent.is_authorized


def test_denied_consent_does_not_authorize():
    assert not _consent(status=ConsentStatus.DENIED).authorizes(
        "case_submission", "office:office-1"
    )


def test_revoked_consent_does_not_authorize():
    assert not _consent(status=ConsentStatus.REVOKED).authorizes(
        "case_submission", "office:office-1"
    )


def test_scope_mismatch_does_not_authorize():
    assert not _consent().authorizes("case_submission", "office:office-2")


def test_purpose_mismatch_does_not_authorize():
    assert not _consent().authorizes("document_preparation", "office:office-1")
