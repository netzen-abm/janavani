import pytest

from src.core.capabilities.escalation_action_service import SharedEscalationActionService
from src.core.capabilities.escalation_resolver import EscalationDecision
from src.core.contracts.authority_discovery import AuthorityCandidate, AuthorityStatus


def verified_authority():
    return AuthorityCandidate("a2", "Next Authority", "department", "IN-KL", "verified", ("official-source",), AuthorityStatus.VERIFIED)


def test_verified_escalation_becomes_user_confirmable_action():
    decision = EscalationDecision("route-1", verified_authority(), "verified escalation route")
    proposal = SharedEscalationActionService().propose(decision)
    assert proposal.action_type == "escalation"
    assert proposal.authority_id == "a2"
    assert proposal.requires_user_confirmation is True


def test_unverified_authority_is_rejected():
    authority = AuthorityCandidate("a2", "Next Authority", "department", "IN-KL", "candidate", (), AuthorityStatus.CANDIDATE)
    decision = EscalationDecision("route-1", authority, "candidate route")
    with pytest.raises(ValueError):
        SharedEscalationActionService().propose(decision)
