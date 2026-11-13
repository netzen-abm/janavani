from src.capabilities.civic_case import CivicCaseCapability, CivicCaseCreateRequest
from src.capabilities.consent import ConsentCapability, PURPOSE_DOCUMENT_PREPARATION, PURPOSE_SUBMISSION
from src.core.civic_case import CaseEventType, CaseType, CivicCase
from src.identity.context import IdentityContext
from src.identity.principal import IdentityMode, Principal
from src.storage.repositories.civic_case import InMemoryCivicCaseRepository
from src.storage.repositories.consent import InMemoryConsentRepository


def _identity(principal_id: str = "telegram:12345", *capabilities: str) -> IdentityContext:
    return IdentityContext(principal=Principal(
        principal_id=principal_id, identity_mode=IdentityMode.ANONYMOUS,
        interface="telegram", capabilities=frozenset(capabilities),
    ))


def _case() -> CivicCase:
    return CivicCase(case_id="JV-001", case_type=CaseType.COMPLAINT,
                     subject="Broken streetlight", narrative="The streetlight has not worked for three nights.",
                     created_by="telegram:12345")


def test_record_submission_consent_persists_and_advances_owned_case():
    cases = InMemoryCivicCaseRepository()
    case_capability = CivicCaseCapability(cases)
    case = case_capability.create(
        CivicCaseCreateRequest(case_type=CaseType.COMPLAINT, subject="Broken streetlight", narrative="The streetlight has not worked for three nights."),
        identity=_identity("telegram:12345", "JNV-CIVIC-COMPLAINT", "case:consent", "case:write", "case:review"),
    ).case
    repository = InMemoryConsentRepository()
    capability = ConsentCapability(repository=repository, case_capability=case_capability)
    actor = _identity("telegram:12345", "case:consent", "case:write", "case:review")
    result = capability.record_submission_consent(
        case.case_id, scope="office:office-1", identity=actor, proof_ref="proof:submission"
    )
    assert result.consent.subject_id == "telegram:12345"
    assert result.consent.purpose == PURPOSE_SUBMISSION
    assert result.consent.scope == ("office:office-1",)
    assert result.consent.is_authorized
    assert result.consent.consent_id in result.case.case.consent_refs
    event_id = f"consent-{result.consent.consent_id}"
    audit_events = [event for event in result.case.case.events if event.event_id == event_id]
    assert len(audit_events) == 1
    assert audit_events[0].event_type is CaseEventType.CONSENT_RECORDED
    assert audit_events[0].actor_id == actor.principal.principal_id
    assert audit_events[0].notes == PURPOSE_SUBMISSION
    assert audit_events[0].source_ref == "proof:submission"
    repeated = capability.record_submission_consent(
        case.case_id, scope="office:office-1", identity=actor, proof_ref="proof:submission"
    )
    assert repeated.consent == result.consent
    assert len([event for event in repeated.case.case.events if event.event_id == event_id]) == 1
    assert repeated.case.case.consent_refs.count(result.consent.consent_id) == 1
    assert repeated.case.case.status.value == "draft"


def test_record_submission_consent_denies_cross_principal_case():
    cases = InMemoryCivicCaseRepository(); cases.save(_case())
    capability = ConsentCapability(repository=InMemoryConsentRepository(), case_capability=CivicCaseCapability(cases))
    try:
        capability.record_submission_consent("JV-001", scope="office:office-1",
            identity=_identity("telegram:99999", "case:consent", "case:write", "case:review"))
    except LookupError:
        pass
    else:
        raise AssertionError("Expected cross-principal consent recording to fail")


def test_record_submission_consent_requires_scope():
    cases = InMemoryCivicCaseRepository(); cases.save(_case())
    capability = ConsentCapability(repository=InMemoryConsentRepository(), case_capability=CivicCaseCapability(cases))
    try:
        capability.record_submission_consent("JV-001", scope=" ",
            identity=_identity("telegram:12345", "case:consent", "case:write", "case:review"))
    except ValueError:
        pass
    else:
        raise AssertionError("Expected empty consent scope to fail closed")


def test_document_preparation_consent_is_not_external_submission_consent():
    cases = InMemoryCivicCaseRepository()
    case_capability = CivicCaseCapability(cases)
    case = case_capability.create(
        CivicCaseCreateRequest(
            case_type=CaseType.COMPLAINT,
            subject="Broken streetlight",
            narrative="The streetlight has not worked for three nights.",
        ),
        identity=_identity("telegram:12345", "JNV-CIVIC-COMPLAINT", "case:consent", "case:write", "case:review"),
    ).case
    capability = ConsentCapability(repository=InMemoryConsentRepository(), case_capability=case_capability)
    actor = _identity("telegram:12345", "case:consent", "case:write", "case:review")

    result = capability.record_document_preparation_consent(
        case.case_id,
        scope="citizen_download_and_self_send",
        identity=actor,
        proof_ref="proof:preparation",
    )

    assert result.consent.purpose == PURPOSE_DOCUMENT_PREPARATION
    assert result.consent.purpose != PURPOSE_SUBMISSION
    assert result.consent.scope == ("citizen_download_and_self_send",)
    assert result.consent.consent_id in result.case.case.consent_refs
    audit_events = [
        event for event in result.case.case.events
        if event.event_id == f"consent-{result.consent.consent_id}"
    ]
    assert len(audit_events) == 1
    assert audit_events[0].event_type is CaseEventType.CONSENT_RECORDED
    assert audit_events[0].notes == PURPOSE_DOCUMENT_PREPARATION
    assert audit_events[0].source_ref == "proof:preparation"
    assert result.case.case.status.value == "draft"


def test_repeated_atomic_preparation_consent_is_idempotent():
    from src.core.civic_case import CaseEvent

    cases = InMemoryCivicCaseRepository()
    case_capability = CivicCaseCapability(cases)
    case = case_capability.create(
        CivicCaseCreateRequest(
            case_type=CaseType.COMPLAINT,
            subject="Broken streetlight",
            narrative="The streetlight has not worked for three nights.",
        ),
        identity=_identity(
            "telegram:12345", "JNV-CIVIC-COMPLAINT", "case:consent", "case:write", "case:review"
        ),
    ).case
    consents = InMemoryConsentRepository()

    class AtomicRecorder:
        calls = 0

        def save_consent_and_case(self, consent, current_case, *, principal_id):
            self.calls += 1
            consents.save(consent, principal_id=principal_id)
            current_case.events.append(CaseEvent(
                event_id=f"consent-{consent.consent_id}",
                case_id=current_case.case_id,
                event_type=CaseEventType.CONSENT_RECORDED,
                occurred_at=consent.created_at,
                actor_id=principal_id,
                source_ref=consent.proof_ref,
                notes=consent.purpose,
            ))
            current_case.version += 1
            cases.save(current_case, principal_id=principal_id)

    atomic = AtomicRecorder()
    capability = ConsentCapability(
        repository=consents,
        case_capability=case_capability,
        atomic_repository=atomic,
    )
    actor = _identity(
        "telegram:12345", "case:consent", "case:write", "case:review"
    )

    first = capability.record_document_preparation_consent(
        case.case_id, scope="citizen_download_and_self_send", identity=actor
    )
    second = capability.record_document_preparation_consent(
        case.case_id, scope="citizen_download_and_self_send", identity=actor
    )

    assert first.consent == second.consent
    assert atomic.calls == 1
    assert second.case.case.consent_refs.count(first.consent.consent_id) == 1
    assert sum(
        event.event_id == f"consent-{first.consent.consent_id}"
        for event in second.case.case.events
    ) == 1
    assert second.case.case.status.value == "draft"
