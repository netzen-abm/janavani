from src.core.capabilities.rti_capability import RTIAction, SharedRTICapability
from src.core.contracts.case import AuthorityReference, Case, VerificationStatus


def test_rti_first_when_information_is_primary_objective():
    result = SharedRTICapability().assess(
        information_objective="obtain sanction and payment records",
        remedy_needed=False,
        information_needed=True,
    )
    assert result.action == RTIAction.RTI_FIRST


def test_complaint_and_rti_can_run_together():
    result = SharedRTICapability().assess(
        information_objective="obtain records while seeking repair",
        remedy_needed=True,
        information_needed=True,
    )
    assert result.action == RTIAction.COMPLAINT_AND_RTI


def test_existing_complaint_can_lead_to_rti_after_trigger():
    result = SharedRTICapability().assess(
        information_objective="obtain file records",
        remedy_needed=True,
        information_needed=True,
        existing_complaint=True,
    )
    assert result.action == RTIAction.RTI_AFTER_TRIGGER


def test_rti_requires_verified_authority():
    case = Case(case_id="case-1", issue_text="Need records")
    try:
        SharedRTICapability().prepare_plan(
            case,
            authority_name="PIO",
            authority_address="Address",
            authority_email="pio@example.gov",
            questions=("Provide the file number",),
            subject="RTI request",
        )
    except ValueError as exc:
        assert "verified" in str(exc)
    else:
        raise AssertionError("unverified authority must not produce RTI plan")
