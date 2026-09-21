"""Persistence and Case-transition helpers for submission."""
from __future__ import annotations

from copy import deepcopy
from dataclasses import replace
from hashlib import sha256

from src.core.civic_case import CaseEvent, CaseEventType
from src.storage.repositories.submission_case_transaction import SubmissionCaseTransactionRepository

ACKNOWLEDGEMENT_EVIDENCE_TYPE = "submission_acknowledgement"


class SubmissionState:
    def __init__(self, capability):
        self.c = capability

    def save(self, record, expected_version=None):
        repo = self.c._submissions
        if repo is None:
            return record
        if expected_version is None:
            repo.save(record)
        else:
            repo.update_if_version(record, expected_version=expected_version)
        return record

    def reserve(self, submission):
        repo = self.c._submissions
        return (submission, False) if repo is None else repo.create_idempotent(submission)

    def with_submitting(self, submission):
        now = self.c._now()
        return replace(
            submission, state="submitting", attempted_at=now,
            updated_at=now, version=submission.version + 1,
        )

    def acknowledgement_evidence(self, case, evidence_id):
        evidence_repo = self.c._evidence
        if evidence_repo is None:
            raise PermissionError("Independent acknowledgement evidence repository is required")
        evidence = evidence_repo.get(evidence_id)
        if evidence is None:
            raise LookupError("Acknowledgement evidence was not found")
        if evidence_id not in case.evidence_refs:
            raise PermissionError("Acknowledgement evidence is not attached to the case")
        if evidence.evidence_type != ACKNOWLEDGEMENT_EVIDENCE_TYPE:
            raise ValueError("Evidence is not an acknowledgement record")
        if evidence.status != "ACTIVE":
            raise ValueError("Acknowledgement evidence is not active")

    def atomic_mutation(
        self, *, submission, expected_submission_version, case,
        expected_case_version, action, identity, source_channel,
        source_ref=None, notes=None,
    ):
        atomic = self.c._atomic
        if atomic is None:
            raise RuntimeError("Atomic Submission-Case repository is required")
        now = self.c._now()
        stage = action.removeprefix("case:")
        event = CaseEvent(
            event_id=self.event_id(submission, stage), case_id=case.case_id,
            event_type={
                "begin_submission": CaseEventType.SUBMITTING,
                "submit": CaseEventType.SUBMITTED,
                "acknowledge": CaseEventType.ACKNOWLEDGED,
            }[stage],
            occurred_at=now, actor_id=identity.principal.principal_id,
            source_channel=source_channel, source_ref=source_ref, notes=notes,
        )
        projection = deepcopy(case)
        method = {
            "begin_submission": projection.begin_submission,
            "submit": projection.submit,
            "acknowledge": projection.acknowledge,
        }[stage]
        kwargs = dict(
            event_id=event.event_id, occurred_at=now,
            actor_id=identity.principal.principal_id,
            source_channel=source_channel,
        )
        if stage == "acknowledge":
            kwargs.update(source_ref=source_ref, notes=notes)
        method(**kwargs)
        result = atomic.persist_mutation(
            submission=submission, expected_submission_version=expected_submission_version,
            case=projection, expected_case_version=expected_case_version,
            event=event, idempotency_key=event.event_id,
        )
        if not result.idempotent_replay:
            for name, value in projection.__dict__.items():
                setattr(case, name, deepcopy(value))
        return result

    def mark_submitted(self, submission, external_ref, request, identity, context):
        now = self.c._now()
        updated = replace(
            submission, state="submitted", submitted_at=now,
            external_reference=external_ref, updated_at=now,
            version=submission.version + 1,
        )
        if self.c._atomic is not None and self.c._submissions is not None:
            case = self.c._cases.get_owned(request.case_id, identity=identity)
            if case is None:
                raise LookupError("Case not found before atomic submission outcome")
            self.atomic_mutation(
                submission=updated, expected_submission_version=submission.version,
                case=case, expected_case_version=case.version,
                action="case:submit", identity=identity,
                source_channel=request.source_channel,
            )
        else:
            self.save(updated, expected_version=submission.version)
            self.c._cases.transition(
                request.case_id, action="case:submit", identity=identity,
                source_channel=request.source_channel,
                execution_context=self.c._child_case_context(
                    context, identity, request.case_id, "case:submit"
                ),
            )
        return updated

    def acknowledge(self, *, case, submission, evidence_id, identity,
                     source_channel, notes, execution_context=None):
        self.acknowledgement_evidence(case, evidence_id)
        now = self.c._now()
        updated = replace(
            submission, state="acknowledged", acknowledged_at=now,
            ack_ref=evidence_id, updated_at=now, version=submission.version + 1,
        )
        if self.c._atomic is not None:
            self.c._validate_execution_context(
                execution_context, identity,
                action="case:acknowledge", resource_id=case.case_id,
            )
            self.atomic_mutation(
                submission=updated, expected_submission_version=submission.version,
                case=case, expected_case_version=case.version,
                action="case:acknowledge", identity=identity,
                source_channel=source_channel, source_ref=evidence_id, notes=notes,
            )
            return
        self.save(updated, expected_version=submission.version)
        self.c._cases.transition(
            case.case_id, action="case:acknowledge", identity=identity,
            source_channel=source_channel, source_ref=evidence_id, notes=notes,
            execution_context=self.c._child_case_context(
                execution_context, identity, case.case_id, "case:acknowledge"
            ),
        )

    @staticmethod
    def event_id(submission, stage):
        digest = sha256(
            f"{submission.idempotency_key}:{stage}".encode()
        ).hexdigest()[:32]
        return f"event-submission-{stage}-{digest}"
