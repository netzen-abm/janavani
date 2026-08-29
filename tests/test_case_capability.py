"""Tests for the canonical shared case capability."""
from src.domain.case import CaseCreate, CaseStatus
from src.services.case_service import CaseService


def test_case_lifecycle_is_channel_neutral():
    service = CaseService()
    case = service.create_case(
        CaseCreate(title="Broken streetlight", description="The streetlight outside our lane has been broken for two weeks.")
    )
    assert case.id.startswith("JNV-")
    assert case.status is CaseStatus.DRAFT

    updated = service.transition(case.id, CaseStatus.READY_FOR_REVIEW)
    assert updated is not None
    assert updated.status is CaseStatus.READY_FOR_REVIEW
    assert any(event["event"] == "status:ready_for_review" for event in updated.timeline)


def test_missing_case_is_safe():
    service = CaseService()
    assert service.get_case("JNV-NOTFOUND") is None
    assert service.transition("JNV-NOTFOUND", CaseStatus.APPROVED) is None
