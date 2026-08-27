"""Channel-neutral Civic Action Workspace workflow state machine."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from typing import Optional
from uuid import uuid4

from .case import Case, CaseStatus
from .submission import Submission, SubmissionStatus


class WorkflowStage(StrEnum):
    ISSUE = "ISSUE"
    UNDERSTANDING = "UNDERSTANDING"
    AUTHORITY = "AUTHORITY"
    ACTION = "ACTION"
    EVIDENCE = "EVIDENCE"
    REVIEW = "REVIEW"
    SUBMISSION = "SUBMISSION"
    TRACKING = "TRACKING"
    OUTCOME = "OUTCOME"


@dataclass(frozen=True, slots=True)
class WorkflowEvent:
    event_id: str
    case_id: str
    stage: WorkflowStage
    occurred_at: datetime
    actor_id: Optional[str] = None
    notes: Optional[str] = None


@dataclass(slots=True)
class CivicActionWorkflow:
    """Orchestrate case progression without owning channel/provider logic."""

    case: Case
    stage: WorkflowStage = WorkflowStage.ISSUE
    submission: Optional[Submission] = None
    workflow_id: str = field(default_factory=lambda: str(uuid4()))
    events: list[WorkflowEvent] = field(default_factory=list)

    def advance(
        self,
        stage: WorkflowStage,
        *,
        actor_id: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> WorkflowEvent:
        """Record a workflow-stage transition and synchronize case state."""
        event = WorkflowEvent(
            event_id=str(uuid4()),
            case_id=self.case.case_id,
            stage=stage,
            occurred_at=datetime.now(timezone.utc),
            actor_id=actor_id,
            notes=notes,
        )
        self.stage = stage
        self.events.append(event)

        if stage is WorkflowStage.REVIEW:
            self.case.transition(CaseStatus.READY, actor_id=actor_id)
        elif stage is WorkflowStage.SUBMISSION:
            self.case.transition(CaseStatus.SUBMITTED, actor_id=actor_id)
            if self.submission is None:
                self.submission = Submission(case_id=self.case.case_id)
        elif stage is WorkflowStage.TRACKING and self.submission:
            if self.submission.status is SubmissionStatus.DRAFT:
                self.submission.transition(SubmissionStatus.SUBMISSION_ATTEMPTED)
        elif stage is WorkflowStage.OUTCOME:
            self.case.transition(CaseStatus.CLOSED, actor_id=actor_id)

        return event


__all__ = ["CivicActionWorkflow", "WorkflowEvent", "WorkflowStage"]
