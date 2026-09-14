from dataclasses import replace

import pytest

from src.capabilities.submission_reconciliation import (
    SubmissionReconciliationCapability,
    SubmissionReconciliationObservation,
)
from src.core.civic_case import CaseStatus
from src.core.submission import SubmissionRecord
from src.identity.context import IdentityContext
from src.identity.principal import AuthenticationMethod, IdentityMode, Principal
from src.storage.repositories.submission import InMemorySubmissionRepository


class FakeCases:
    def __init__(self, case):
        self.case = case
        self.transitions = []

    def get_owned(self, case_id, *, identity):
        return self.case if self.case.case_id == case_id and self.case.created_by == identity.principal.principal_id else None

    def transition(self, case_id, *, action, identity, **kwargs):
        self.transitions.append((case_id, action, kwargs))
        self.case.status = CaseStatus.SUBMITTED


class FakeSource:
    def __init__(self, observation):
        self.observation = observation
        self.seen = None

    def reconcile(self, submission):
        self.seen = submission
        return self.observation


def identity(principal_id="citizen-a"):
    return IdentityContext(
        principal=Principal(
            principal_id=principal_id,
            mode=IdentityMode.AUTHENTICATED,
            authentication_method=AuthenticationMethod.PASSKEY,
            capabilities=frozenset({"case:submit"}),
        )
    )


def submission(state="unknown"):
    return SubmissionRecord.new(
        submission_id="sub-1", case_id="case-1", destination_ref="office-1",
        document_ref="doc-1", channel="web", state=state, idempotency_key="idem-1",
    )


def case_for(owner="citizen-a"):
    from src.core.civic_case import CaseType, CivicCase
    return CivicCase(
        case_id="case-1", case_type=CaseType.COMPLAINT, subject="Issue",
        narrative="Details", created_by=owner, status=CaseStatus.SUBMITTING,
    )


def test_submitted_observation_updates_submission_and_case():
    repo = InMemorySubmissionRepository()
    repo.save(submission())
    source = FakeSource(SubmissionReconciliationObservation(
        outcome="submitted", observed_at="2026-09-14T00:00:00+00:00",
        source_ref="provider-status-1", external_reference="ext-1",
    ))
    cases = FakeCases(case_for())
    result = SubmissionReconciliationCapability(cases, repo, source).reconcile("sub-1", identity=identity())
    updated = repo.get("sub-1")

    assert updated is not None
    assert updated.state == "submitted"
    assert updated.external_reference == "ext-1"
    assert updated.idempotency_key == "idem-1"
    assert updated.version == 2
    assert result.case.status is CaseStatus.SUBMITTED
    assert cases.transitions[0][1] == "case:submit"


def test_failed_observation_is_persisted_without_case_success():
    repo = InMemorySubmissionRepository()
    repo.save(submission())
    source = FakeSource(SubmissionReconciliationObservation(
        outcome="failed", observed_at="2026-09-14T00:00:00+00:00", source_ref="provider-status-2",
    ))
    cases = FakeCases(case_for())
    result = SubmissionReconciliationCapability(cases, repo, source).reconcile("sub-1", identity=identity())

    assert repo.get("sub-1").state == "failed"
    assert result.case.status is CaseStatus.SUBMITTING
    assert cases.transitions == []


def test_non_unknown_submission_is_rejected():
    repo = InMemorySubmissionRepository()
    repo.save(submission("submitted"))
    source = FakeSource(SubmissionReconciliationObservation(
        outcome="submitted", observed_at="2026-09-14T00:00:00+00:00", source_ref="provider-status-3",
    ))
    with pytest.raises(ValueError, match="Only an unknown submission"):
        SubmissionReconciliationCapability(FakeCases(case_for()), repo, source).reconcile("sub-1", identity=identity())


def test_cross_principal_case_is_denied():
    repo = InMemorySubmissionRepository()
    repo.save(submission())
    source = FakeSource(SubmissionReconciliationObservation(
        outcome="submitted", observed_at="2026-09-14T00:00:00+00:00", source_ref="provider-status-4",
    ))
    with pytest.raises(LookupError, match="Case not found"):
        SubmissionReconciliationCapability(FakeCases(case_for("citizen-b")), repo, source).reconcile("sub-1", identity())
