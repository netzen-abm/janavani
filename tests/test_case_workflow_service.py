from src.application.case_workflow import CaseWorkflowService
from src.domain.authority import Authority
from src.domain.consent import Consent
from src.domain.evidence import Evidence, EvidenceKind
from src.domain.submission import SubmissionStatus
from src.storage.case_memory_repository import (
    MemoryAuthorityRepository,
    MemoryCaseRepository,
    MemoryEvidenceRepository,
    MemorySubmissionRepository,
)


def make_service() -> CaseWorkflowService:
    return CaseWorkflowService(
        cases=MemoryCaseRepository(),
        evidence=MemoryEvidenceRepository(),
        authorities=MemoryAuthorityRepository(),
        submissions=MemorySubmissionRepository(),
    )


def test_case_workflow_requires_review_and_approval_before_submission():
    service = make_service()
    case = service.create_case("Road drainage failure")
    evidence = Evidence.create(case.id, EvidenceKind.PHOTO, "Blocked drain", "citizen", provenance=["user-capture"])
    service.attach_evidence(case.id, evidence)
    authority = Authority.create("Municipal Engineering Office", "office")
    service.authorities.save(authority)  # type: ignore[attr-defined]
    service.select_authority(case.id, authority.authority_id)

    try:
        service.create_submission(case.id, "authority:municipal-engineering")
        assert False, "submission must require explicit approval"
    except ValueError as exc:
        assert "explicit approval" in str(exc)

    service.request_submission_approval(case.id)
    service.approve_submission(case.id)
    submission = service.create_submission(case.id, "authority:municipal-engineering")

    assert submission.status == SubmissionStatus.CREATED
    assert submission.case_id == case.id


def test_submission_delivery_requires_reference():
    service = make_service()
    case = service.create_case("Water supply interruption")
    evidence = Evidence.create(case.id, EvidenceKind.RECORD, "Service notice", "citizen", provenance=["user-upload"])
    service.attach_evidence(case.id, evidence)
    authority = Authority.create("Water Authority", "office")
    service.authorities.save(authority)  # type: ignore[attr-defined]
    service.select_authority(case.id, authority.authority_id)
    service.request_submission_approval(case.id)
    service.approve_submission(case.id)
    submission = service.create_submission(case.id, "authority:water")

    service.mark_submission_queued(submission.submission_id)
    service.mark_submission_transmitting(submission.submission_id)

    try:
        service.record_submission_sent(submission.submission_id, adapter_id="test", reference="")
        assert False, "sent state must require provider reference"
    except ValueError as exc:
        assert "requires provider/delivery reference" in str(exc)

    service.record_submission_sent(submission.submission_id, adapter_id="test", reference="provider-1")
    assert service._submission(submission.submission_id).status == SubmissionStatus.SENT


def test_consent_must_belong_to_case_and_be_active():
    service = make_service()
    case = service.create_case("Unsafe road")
    consent = Consent.grant(
        case.id,
        "CIVIC.COMPLAINT.DRAFT",
        "draft complaint",
        source_channel="web",
    )
    service.record_consent(case.id, consent)
    assert consent.consent_id in case.consent_ids
