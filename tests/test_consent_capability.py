from src.capabilities.civic_case import CivicCaseCapability
from src.capabilities.consent import ConsentCapability, PURPOSE_SUBMISSION
from src.core.civic_case import CaseType, CivicCase
from src.identity.context import IdentityContext
from src.identity.principal import IdentityMode, Principal
from src.storage.repositories.civic_case import InMemoryCivicCaseRepository
from src.storage.repositories.consent import InMemoryConsentRepository


def _identity(principal_id: str = "telegram:12345", *capabilities: str) -> IdentityContext:
    return IdentityContext(
        principal=Principal(
            principal_id=principal_id,
            identity_mode=IdentityMode.ANONYMOUS,
            interface="telegram",
            capabilities=frozenset(capabilities),
        )
    )


def _case() -> CivicCase:
    return CivicCase(
        case_id="JV-001",
        case_type=CaseType.COMPLAINT,
        subject="Broken streetlight",
        narrative="The streetlight has not worked for three nights.",
        created_by="telegram:12345",
    )


def test_record_submission_consent_persists_canonical_consent_and_advances_case() -> None:
    case_repository = InMemoryCivicCaseRepository()
    case_repository.save(_case())
    case_capability = CivicCaseCapability(case_repository)
    consent_repository = InMemoryConsentRepository()
    capability = ConsentCapability(
        repository=consent_repository,
        case_capability=case_capability,
    )

    result = capability.record_submission_consent(
        "JV-001",
        scope="office:office-1",
        identity=_identity("telegram:12345", "case:consent", "case:write", "case:review"),
    )

    assert result.consent.subject_id == "telegram:12345"
    assert result.consent.purpose == PURPOSE_SUBMISSION
    assert result.consent.scope == ("office:office-1",)
    assert result.consent.is_authorized
    assert result.consent.consent_id in result.case.case.consent_refs
    assert result.case.case.status.value == "ready"
    assert consent_repository.get(result.consent.consent_id) is result.consent


def test_record_submission_consent_denies_cross_principal_case() -> None:
    case_repository = InMemoryCivicCaseRepository()
    case_repository.save(_case())
    capability = ConsentCapability(
        repository=InMemoryConsentRepository(),
        case_capability=CivicCaseCapability(case_repository),
    )

    try:
        capability.record_submission_consent(
            "JV-001",
            scope="office:office-1",
            identity=_identity("telegram:99999", "case:consent", "case:write", "case:review"),
        )
    except LookupError:
        pass
    else:
        raise AssertionError("Expected cross-principal consent recording to fail")


def test_record_submission_consent_requires_scope() -> None:
    case_repository = InMemoryCivicCaseRepository()
    case_repository.save(_case())
    capability = ConsentCapability(
        repository=InMemoryConsentRepository(),
        case_capability=CivicCaseCapability(case_repository),
    )

    try:
        capability.record_submission_consent(
            "JV-001",
            scope=" ",
            identity=_identity("telegram:12345", "case:consent", "case:write", "case:review"),
        )
    except ValueError:
        pass
    else:
        raise AssertionError("Expected empty consent scope to fail closed")
