from types import SimpleNamespace

from src.capabilities.civic_action_vertical_slice import CivicActionVerticalSlice
from src.capabilities.escalation import EscalationAction, EscalationCapability, EscalationContext, EscalationStatus
from src.core.civic_case import CaseStatus, CaseType, CivicCase


def _case(status=CaseStatus.ACKNOWLEDGED):
    return CivicCase(
        case_id="case-test",
        case_type=CaseType.COMPLAINT,
        subject="Test matter",
        narrative="Test narrative",
        created_by="citizen:test",
        status=status,
    )


def test_vertical_slice_exposes_canonical_escalation_decision():
    slice_ = object.__new__(CivicActionVerticalSlice)
    slice_._deps = SimpleNamespace(escalation_capability=EscalationCapability())

    result = slice_.recommend_escalation(
        EscalationContext(case=_case(), user_report="unsatisfactory")
    )

    assert result.action is EscalationAction.ADMINISTRATIVE_HEAD
    assert result.status is EscalationStatus.RECOMMENDED
