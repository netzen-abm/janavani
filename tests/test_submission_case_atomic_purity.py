from dataclasses import dataclass

import pytest

from src.capabilities.submission import SubmissionCapability
from src.core.civic_case import CaseStatus, CaseType, CivicCase
from src.core.submission import SubmissionRecord
from src.identity.context import IdentityContext
from src.identity.principal import AuthenticationMethod, IdentityMode, Principal


class FailingAtomicRepository:
    def __init__(self) -> None:
        self.received_case = None

    def persist_mutation(self, *, submission, expected_submission_version, case,
                         expected_case_version, event, idempotency_key):
        self.received_case = case
        raise RuntimeError("simulated transaction rollback")


@dataclass
class DummyConsentRepository:
    pass


def _identity() -> IdentityContext:
    return IdentityContext(
        principal=Principal(
            principal_id="citizen-1",
            identity_mode=IdentityMode.AUTHENTICATED,
            authentication_method=AuthenticationMethod.PASSKEY,
            capabilities=frozenset({"case:submit"}),
        )
    )


def _case() -> CivicCase:
    return CivicCase(
        case_id="case-1",
        case_type=CaseType.COMPLAINT,
        subject="Broken road",
        narrative="The road is unsafe.",
        created_by="citizen-1",
        status=CaseStatus.READY,
        version=7,
    )


def test_atomic_case_mutation_does_not_mutate_caller_on_persistence_failure():
    atomic = FailingAtomicRepository()
    capability = SubmissionCapability(
        case_capability=None,
        consent_repository=DummyConsentRepository(),
        transport=object(),
        submission_case_transaction_repository=atomic,
    )
    case = _case()
    submission = SubmissionRecord.new(
        submission_id="sub-1",
        case_id=case.case_id,
        destination_ref="office-1",
        document_ref="doc-1",
        channel="test",
        idempotency_key="idem-1",
    )

    with pytest.raises(RuntimeError, match="simulated transaction rollback"):
        capability._atomic_case_mutation(
            submission=submission,
            expected_submission_version=0,
            case=case,
            expected_case_version=case.version,
            action="case:begin_submission",
            identity=_identity(),
            source_channel="test",
        )

    assert case.status is CaseStatus.READY
    assert case.version == 7
    assert case.events == []
    assert atomic.received_case is not case
    assert atomic.received_case.status is CaseStatus.SUBMITTING
    assert len(atomic.received_case.events) == 1
