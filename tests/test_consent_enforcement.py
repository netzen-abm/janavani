from src.access.consent import ConsentRequiredError, ConsentRequirement, require_consent
from src.core.consent import Consent, ConsentGrantType, ConsentStatus
from src.storage.repositories.consent import InMemoryConsentRepository


def _consent(status: ConsentStatus, scope: tuple[str, ...] = ("submit",)) -> Consent:
    return Consent(
        consent_id="consent-1",
        subject_id="subject-1",
        purpose="civic_submission",
        scope=scope,
        grant_type=ConsentGrantType.EXPLICIT,
        status=status,
        created_at="2026-09-09T00:00:00Z",
        revoked_at="2026-09-09T01:00:00Z" if status is ConsentStatus.REVOKED else None,
    )


def test_granted_consent_authorizes_matching_purpose_and_scope() -> None:
    repository = InMemoryConsentRepository()
    repository.save(_consent(ConsentStatus.GRANTED))

    require_consent(
        repository,
        ConsentRequirement(
            subject_id="subject-1",
            purpose="civic_submission",
            scope="submit",
        ),
    )


def test_missing_consent_fails_closed() -> None:
    repository = InMemoryConsentRepository()

    try:
        require_consent(
            repository,
            ConsentRequirement(
                subject_id="subject-1",
                purpose="civic_submission",
                scope="submit",
            ),
        )
    except ConsentRequiredError:
        return
    raise AssertionError("missing consent must fail closed")


def test_denied_consent_does_not_authorize() -> None:
    repository = InMemoryConsentRepository()
    repository.save(_consent(ConsentStatus.DENIED))

    try:
        require_consent(
            repository,
            ConsentRequirement(
                subject_id="subject-1",
                purpose="civic_submission",
                scope="submit",
            ),
        )
    except ConsentRequiredError:
        return
    raise AssertionError("denied consent must not authorize")


def test_scope_mismatch_does_not_authorize() -> None:
    repository = InMemoryConsentRepository()
    repository.save(_consent(ConsentStatus.GRANTED, scope=("draft",)))

    try:
        require_consent(
            repository,
            ConsentRequirement(
                subject_id="subject-1",
                purpose="civic_submission",
                scope="submit",
            ),
        )
    except ConsentRequiredError:
        return
    raise AssertionError("scope mismatch must not authorize")
