from src.capabilities.civic_case import CivicCaseCapability, CivicCaseCreateRequest
from src.capabilities.consent import ConsentCapability, PURPOSE_DOCUMENT_PREPARATION, PURPOSE_SUBMISSION
from src.core.consent import Consent, ConsentGrantType, ConsentStatus
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
        case.case_id, scope="office:office-1", identity=actor, action_id="webhook-update-101", proof_ref="proof:submission"
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
        case.case_id, scope="office:office-1", identity=actor, action_id="webhook-update-101", proof_ref="proof:submission"
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
            identity=_identity("telegram:99999", "case:consent", "case:write", "case:review"),
            action_id="unauthorized-update")
    except LookupError:
        pass
    else:
        raise AssertionError("Expected cross-principal consent recording to fail")


def test_record_submission_consent_requires_scope():
    cases = InMemoryCivicCaseRepository(); cases.save(_case())
    capability = ConsentCapability(repository=InMemoryConsentRepository(), case_capability=CivicCaseCapability(cases))
    try:
        capability.record_submission_consent("JV-001", scope=" ",
            identity=_identity("telegram:12345", "case:consent", "case:write", "case:review"),
            action_id="empty-scope-update")
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
        action_id="web-preparation-1",
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


def test_repeated_preparation_consent_reuses_one_atomic_action():
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
    capability = ConsentCapability(repository=consents, case_capability=case_capability)
    actor = _identity("telegram:12345", "case:consent", "case:write", "case:review")

    first = capability.record_document_preparation_consent(
        case.case_id, scope="citizen_download_and_self_send",
        identity=actor, action_id="same-explicit-action",
    )
    second = capability.record_document_preparation_consent(
        case.case_id, scope="citizen_download_and_self_send",
        identity=actor, action_id="same-explicit-action",
    )

    assert first.consent == second.consent
    assert len(consents.list_for_subject("telegram:12345")) == 1
    assert second.case.case.consent_refs.count(first.consent.consent_id) == 1
    assert sum(
        event.event_id == f"consent-{first.consent.consent_id}"
        for event in second.case.case.events
    ) == 1
    assert second.case.case.status.value == "draft"


def test_distinct_explicit_actions_create_distinct_historical_grants():
    cases = InMemoryCivicCaseRepository()
    case_capability = CivicCaseCapability(cases)
    case = case_capability.create(
        CivicCaseCreateRequest(
            case_type=CaseType.COMPLAINT,
            subject="Streetlight",
            narrative="A streetlight is broken.",
        ),
        identity=_identity("telegram:12345", "JNV-CIVIC-COMPLAINT", "case:consent", "case:write"),
    ).case
    repository = InMemoryConsentRepository()
    capability = ConsentCapability(repository=repository, case_capability=case_capability)
    actor = _identity("telegram:12345", "case:consent", "case:write")

    first = capability.record_document_preparation_consent(
        case.case_id, scope="citizen_download_and_self_send",
        identity=actor, action_id="citizen-confirmation-1",
    )
    second = capability.record_document_preparation_consent(
        case.case_id, scope="citizen_download_and_self_send",
        identity=actor, action_id="citizen-confirmation-2",
    )

    assert first.consent.consent_id != second.consent.consent_id
    assert len(repository.list_for_subject("telegram:12345")) == 2
    assert len([
        event for event in second.case.case.events
        if event.event_type is CaseEventType.CONSENT_RECORDED
    ]) == 2


def test_concurrent_retries_of_one_consent_action_create_one_grant_and_event():
    from concurrent.futures import ThreadPoolExecutor

    cases = InMemoryCivicCaseRepository()
    case_capability = CivicCaseCapability(cases)
    case = case_capability.create(
        CivicCaseCreateRequest(
            case_type=CaseType.COMPLAINT,
            subject="Road damage",
            narrative="The road is damaged.",
        ),
        identity=_identity("telegram:12345", "JNV-CIVIC-COMPLAINT", "case:consent", "case:write"),
    ).case
    repository = InMemoryConsentRepository()
    capability = ConsentCapability(repository=repository, case_capability=case_capability)
    actor = _identity("telegram:12345", "case:consent", "case:write")

    def record():
        return capability.record_document_preparation_consent(
            case.case_id, scope="citizen_download_and_self_send",
            identity=actor, action_id="telegram-update:concurrent-1",
        )

    with ThreadPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(lambda _: record(), range(24)))

    grant_ids = {result.consent.consent_id for result in results}
    assert len(grant_ids) == 1
    assert len(repository.list_for_subject("telegram:12345")) == 1
    current = case_capability.get_owned(case.case_id, identity=actor)
    assert current is not None
    assert current.consent_refs.count(next(iter(grant_ids))) == 1
    assert sum(event.event_id == f"consent-{next(iter(grant_ids))}" for event in current.events) == 1


def test_reused_action_id_with_changed_scope_fails_closed():
    from src.storage.repositories.consent_case_atomic import ConsentIdempotencyConflictError

    cases = InMemoryCivicCaseRepository()
    case_capability = CivicCaseCapability(cases)
    case = case_capability.create(
        CivicCaseCreateRequest(
            case_type=CaseType.COMPLAINT,
            subject="Road damage",
            narrative="The road is damaged.",
        ),
        identity=_identity("telegram:12345", "JNV-CIVIC-COMPLAINT", "case:consent", "case:write"),
    ).case
    repository = InMemoryConsentRepository()
    capability = ConsentCapability(repository=repository, case_capability=case_capability)
    actor = _identity("telegram:12345", "case:consent", "case:write")
    capability.record_document_preparation_consent(
        case.case_id, scope="office:one", identity=actor, action_id="same-action-key"
    )
    try:
        capability.record_document_preparation_consent(
            case.case_id, scope="office:two", identity=actor, action_id="same-action-key"
        )
    except ConsentIdempotencyConflictError:
        pass
    else:
        raise AssertionError("Reusing an action key with another scope must fail")


def test_attaching_existing_consent_requires_case_consent_capability():
    cases = InMemoryCivicCaseRepository()
    case_capability = CivicCaseCapability(cases)
    owner = _identity(
        "telegram:12345",
        "JNV-CIVIC-COMPLAINT",
        "case:consent",
        "case:write",
        "case:review",
    )
    case = case_capability.create(
        CivicCaseCreateRequest(
            case_type=CaseType.COMPLAINT,
            subject="Consent authorization",
            narrative="Synthetic case for consent attachment authorization.",
        ),
        identity=owner,
    ).case

    scope = "office:office-1"
    consent = Consent(
        consent_id=ConsentCapability._consent_id(case.case_id, PURPOSE_SUBMISSION, scope),
        subject_id=owner.principal.principal_id,
        purpose=PURPOSE_SUBMISSION,
        scope=(scope,),
        grant_type=ConsentGrantType.EXPLICIT,
        status=ConsentStatus.GRANTED,
        created_at="2026-09-09T10:01:00Z",
        proof_ref="proof:stored-grant",
    )
    repository = InMemoryConsentRepository()
    repository.save(consent, principal_id=owner.principal.principal_id)
    capability = ConsentCapability(repository=repository, case_capability=case_capability)

    unauthorized_identities = (
        _identity("telegram:12345", "case:write", "case:review"),
        _identity("telegram:12345", "case:consent", "case:review"),
    )
    for unauthorized in unauthorized_identities:
        try:
            capability.attach_existing_consent(
                case.case_id, consent.consent_id, identity=unauthorized
            )
        except PermissionError:
            pass
        else:
            raise AssertionError("Expected attachment to require case:consent and case:write")

    current = case_capability.get_owned(case.case_id, identity=owner)
    assert current is not None
    assert consent.consent_id not in current.consent_refs
    assert all(event.event_id != f"consent-{consent.consent_id}" for event in current.events)

 

def test_case_capability_does_not_expose_unverified_consent_id_mutation():
    cases = InMemoryCivicCaseRepository()
    case_capability = CivicCaseCapability(cases)

    assert not hasattr(case_capability, "add_consent")
    assert hasattr(case_capability, "_record_verified_consent")


def test_expired_consent_can_be_replaced_by_a_new_version_without_overwriting_history():
    cases = InMemoryCivicCaseRepository()
    case_capability = CivicCaseCapability(cases)
    owner = _identity(
        "telegram:12345", "JNV-CIVIC-COMPLAINT", "case:consent", "case:write", "case:review"
    )
    case = case_capability.create(
        CivicCaseCreateRequest(
            case_type=CaseType.COMPLAINT,
            subject="Consent renewal",
            narrative="Synthetic consent renewal case.",
        ),
        identity=owner,
    ).case
    repository = InMemoryConsentRepository()
    scope = "office:office-renewal"
    base_id = ConsentCapability._consent_id(case.case_id, PURPOSE_SUBMISSION, scope)
    expired = Consent(
        consent_id=base_id,
        subject_id=owner.principal.principal_id,
        purpose=PURPOSE_SUBMISSION,
        scope=(scope,),
        grant_type=ConsentGrantType.EXPLICIT,
        status=ConsentStatus.GRANTED,
        created_at="2026-01-01T00:00:00+00:00",
        expires_at="2026-01-02T00:00:00+00:00",
        proof_ref="proof:expired",
    )
    repository.save(expired)
    capability = ConsentCapability(repository=repository, case_capability=case_capability)

    renewed = capability.record_submission_consent(
        case.case_id, scope=scope, identity=owner, action_id="renewal-action-1", proof_ref="proof:renewed"
    )

    assert renewed.consent.consent_id != expired.consent_id
    assert renewed.consent.consent_id.startswith(f"{base_id}:a:")
    assert renewed.consent.is_authorized
    assert repository.get(base_id) == expired
    assert repository.get(base_id).is_authorized is False

    repeated = capability.record_submission_consent(
        case.case_id, scope=scope, identity=owner, action_id="renewal-action-1", proof_ref="proof:renewed"
    )
    assert repeated.consent.consent_id == renewed.consent.consent_id
    assert len(repository.list_for_subject(owner.principal.principal_id)) == 2
    current = case_capability.get_owned(case.case_id, identity=owner)
    assert current is not None
    assert current.consent_refs.count(renewed.consent.consent_id) == 1


def test_new_explicit_consent_does_not_overwrite_a_revoked_grant():
    cases = InMemoryCivicCaseRepository()
    case_capability = CivicCaseCapability(cases)
    owner = _identity(
        "telegram:12345", "JNV-CIVIC-COMPLAINT", "case:consent", "case:write", "case:review"
    )
    case = case_capability.create(
        CivicCaseCreateRequest(
            case_type=CaseType.COMPLAINT,
            subject="Revoked consent",
            narrative="Synthetic revoked consent case.",
        ),
        identity=owner,
    ).case
    repository = InMemoryConsentRepository()
    scope = "office:office-revocation"
    base_id = ConsentCapability._consent_id(case.case_id, PURPOSE_SUBMISSION, scope)
    revoked = Consent(
        consent_id=base_id,
        subject_id=owner.principal.principal_id,
        purpose=PURPOSE_SUBMISSION,
        scope=(scope,),
        grant_type=ConsentGrantType.EXPLICIT,
        status=ConsentStatus.REVOKED,
        created_at="2026-01-01T00:00:00+00:00",
        revoked_at="2026-01-02T00:00:00+00:00",
        proof_ref="proof:revoked",
    )
    repository.save(revoked)
    capability = ConsentCapability(repository=repository, case_capability=case_capability)

    fresh = capability.record_submission_consent(
        case.case_id, scope=scope, identity=owner, action_id="new-explicit-choice-1", proof_ref="proof:new-explicit-choice"
    )

    assert fresh.consent.consent_id != revoked.consent_id
    assert fresh.consent.is_authorized
    assert repository.get(base_id) == revoked
    assert repository.get(base_id).status is ConsentStatus.REVOKED
