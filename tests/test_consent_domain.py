import pytest

from core.consent import Consent, ConsentGrantType, ConsentStatus
from storage.repositories.consent import InMemoryConsentRepository


def make_consent(**overrides):
    values = {
        "consent_id": "consent-1",
        "subject_id": "subject-1",
        "purpose": "submit civic case",
        "scope": ("case_submission",),
        "grant_type": ConsentGrantType.EXPLICIT,
        "status": ConsentStatus.GRANTED,
        "created_at": "2026-09-06T00:00:00Z",
    }
    values.update(overrides)
    return Consent(**values)


def test_granted_consent_authorizes_exact_purpose_and_scope():
    consent = make_consent()
    assert consent.is_authorized
    assert consent.authorizes("submit civic case", "case_submission")
    assert not consent.authorizes("other purpose", "case_submission")
    assert not consent.authorizes("submit civic case", "other_scope")


def test_denied_revoked_and_expired_consent_are_not_authorized():
    for status, extra in [
        (ConsentStatus.DENIED, {}),
        (ConsentStatus.REVOKED, {"revoked_at": "2026-09-06T01:00:00Z"}),
        (ConsentStatus.EXPIRED, {}),
    ]:
        assert not make_consent(status=status, **extra).is_authorized


def test_revoked_consent_requires_revocation_timestamp():
    with pytest.raises(ValueError, match="revoked_at"):
        make_consent(status=ConsentStatus.REVOKED)


def test_required_consent_cannot_have_empty_scope():
    with pytest.raises(ValueError, match="scope"):
        make_consent(scope=())


def test_not_required_grant_type_can_have_empty_scope():
    consent = make_consent(
        scope=(),
        grant_type=ConsentGrantType.NOT_REQUIRED,
        status=ConsentStatus.GRANTED,
    )
    assert consent.is_authorized


def test_consent_identifier_is_idempotent_in_repository():
    repository = InMemoryConsentRepository()
    consent = make_consent()
    repository.save(consent)
    repository.save(consent)
    assert repository.get(consent.consent_id) == consent


def test_repository_rejects_conflicting_reuse_of_consent_id():
    repository = InMemoryConsentRepository()
    repository.save(make_consent())
    with pytest.raises(ValueError, match="different content"):
        repository.save(make_consent(purpose="different purpose"))


def test_repository_lists_only_subject_consents():
    repository = InMemoryConsentRepository()
    first = make_consent(consent_id="consent-1", subject_id="subject-1")
    second = make_consent(consent_id="consent-2", subject_id="subject-2")
    repository.save(first)
    repository.save(second)
    assert repository.list_for_subject("subject-1") == [first]
