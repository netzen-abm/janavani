from src.domain import Case, CaseStatus
from src.domain.submission import SubmissionStatus
from src.domain.workflow import CivicActionWorkflow, WorkflowStage


def test_workflow_progression_creates_submission_and_case_events():
    workflow = CivicActionWorkflow(Case(subject="Road damage"))

    workflow.advance(WorkflowStage.UNDERSTANDING, actor_id="citizen-1")
    workflow.advance(WorkflowStage.EVIDENCE, actor_id="citizen-1")
    workflow.advance(WorkflowStage.REVIEW, actor_id="citizen-1")
    workflow.advance(WorkflowStage.SUBMISSION, actor_id="citizen-1")

    assert workflow.stage is WorkflowStage.SUBMISSION
    assert workflow.case.status is CaseStatus.SUBMITTED
    assert workflow.submission is not None
    assert workflow.submission.case_id == workflow.case.case_id
    assert [event.stage for event in workflow.events] == [
        WorkflowStage.UNDERSTANDING,
        WorkflowStage.EVIDENCE,
        WorkflowStage.REVIEW,
        WorkflowStage.SUBMISSION,
    ]


def test_tracking_does_not_claim_confirmation():
    workflow = CivicActionWorkflow(Case(subject="Water outage"))

    workflow.advance(WorkflowStage.SUBMISSION)
    workflow.advance(WorkflowStage.TRACKING)

    assert workflow.submission is not None
    assert workflow.submission.status is SubmissionStatus.SUBMISSION_ATTEMPTED
    assert workflow.submission.status is not SubmissionStatus.CONFIRMED
