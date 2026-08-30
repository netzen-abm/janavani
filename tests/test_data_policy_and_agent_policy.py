from src.capabilities.data_policy import DataClass, DataPolicy
from src.capabilities.agent_policy import AgentToolPolicy


def test_public_context_can_be_sanitized():
    result = DataPolicy().sanitize_public_context(
        {"issue_type": "road maintenance", "language": "en"},
        {"issue_type": DataClass.PUBLIC, "language": DataClass.NON_SENSITIVE},
    )
    assert result.allowed is True


def test_private_data_is_rejected_from_public_context():
    result = DataPolicy().sanitize_public_context(
        {"name": "Citizen"}, {"name": DataClass.PERSONAL}
    )
    assert result.allowed is False


def test_authorized_non_sensitive_processing_requires_purpose():
    policy = DataPolicy()
    fields = {"issue_type": "road"}
    classes = {"issue_type": DataClass.NON_SENSITIVE}
    assert policy.authorize(fields, classes, user_authorized=True).allowed is False
    assert policy.authorize(fields, classes, user_authorized=True, purpose="drafting").allowed is True


def test_agent_tool_scope_and_confirmation_are_separate():
    policy = AgentToolPolicy()
    allowed = frozenset({"submit_external"})
    assert policy.authorize("submit_external", allowed).allowed is False
    assert policy.authorize("submit_external", allowed).requires_confirmation is True
    assert policy.authorize("submit_external", allowed, user_confirmed=True).allowed is True


def test_unknown_agent_tool_is_denied():
    decision = AgentToolPolicy().authorize("unknown", frozenset({"unknown"}))
    assert decision.allowed is False
