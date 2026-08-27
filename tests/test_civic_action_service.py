from src.application import CivicActionService
from src.domain import CaseStatus
from src.domain.authority import AuthorityReference
from src.domain.evidence import Evidence, EvidenceKind, VerificationStatus
from src.domain.workflow import WorkflowStage


def test_service_builds_first_vertical_slice_without_channel_dependencies():
    service = CivicActionService()
    workflow = service.create_case(
        subject="Streetlight failure",
        narrative="The streetlight has been broken for one week.",
        actor_id="citizen-1",
        jurisdiction="ward-12",
    )

    evidence = Evidence(kind=EvidenceKind.IMAGE, title="Broken streetlight")
    service.attach_evidence(workflow, evidence, actor_id="citizen-1")
    service.attach_authority(
        workflow,
        AuthorityReference(name="Municipal Electrical Office", office_id="office-12"),
        actor_id="citizen-1",
    )
    service.prepare_review(workflow, actor_id="citizen-1")

    assert workflow.stage is WorkflowStage.REVIEW
    assert workflow.case.status is CaseStatus.READY
    assert evidence.verification_status is VerificationStatus.UNVERIFIED
    assert workflow.case.evidence_refs == [evidence.evidence_id]
    assert workflow.case.related_office_id == "office-12"


def test_service_requires_explicit_actor_for_submission_approval():
    service = CivicActionService()
    workflow = service.create_case(subject="Water outage")

    try:
        service.approve_for_submission(workflow, actor_id="")
    except ValueError as exc:
        assert "actor_id" in str(exc)
    else:
        raise AssertionError("approval without an actor must fail")


def test_service_creates_submission_only_after_approval():
    service = CivicActionService()
    workflow = service.create_case(subject="Road damage", actor_id="citizen-1")

    assert workflow.submission is None

    service.approve_for_submission(workflow, actor_id="citizen-1")

    assert workflow.submission is not None
    assert workflow.stage is WorkflowStage.SUBMISSION
    assert workflow.case.status is CaseStatus.SUBMITTED
