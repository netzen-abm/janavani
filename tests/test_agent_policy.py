import pytest

from src.capabilities.agent_policy import AgentToolDenied, AgentToolRequest, authorize_agent_tool
from src.capabilities.consent_policy import CapabilityPolicy


def policy():
    return CapabilityPolicy(
        capability="citizen.document.generate",
        allowed_fields=frozenset({"issue_text"}),
        consent_required_fields=frozenset(),
        allowed_providers=frozenset({"local"}),
        allowed_processing_modes=frozenset({"deterministic"}),
    )


def request(**kwargs):
    values = dict(
        agent_id="agent-1",
        tool="document_builder",
        capability="citizen.document.generate",
        purpose="prepare citizen document",
        requested_fields=frozenset({"issue_text"}),
        provider="local",
        processing_mode="deterministic",
    )
    values.update(kwargs)
    return AgentToolRequest(**values)


def test_agent_request_within_scope_is_allowed():
    authorize_agent_tool(request(), policy())


def test_agent_cannot_request_unapproved_field():
    with pytest.raises(AgentToolDenied):
        authorize_agent_tool(request(requested_fields=frozenset({"issue_text", "phone"})), policy())


def test_agent_provider_mismatch_is_denied():
    with pytest.raises(AgentToolDenied):
        authorize_agent_tool(request(provider="external-provider"), policy())


def test_agent_missing_purpose_is_denied():
    with pytest.raises(AgentToolDenied):
        authorize_agent_tool(request(purpose=""), policy())
