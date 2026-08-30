from src.capabilities.agent_audit import AgentDecision, make_agent_audit_event


def test_agent_audit_event_is_minimized():
    event = make_agent_audit_event(
        capability_id="ai.drafting",
        tool_id="draft_document",
        decision=AgentDecision.ALLOWED,
        risk="TRANSFORMATIVE",
        reason="policy scope matched",
        consent_grant_id="grant-1",
        provider_id="local.ai",
    )
    record = event.to_record()
    assert record["capability_id"] == "ai.drafting"
    assert record["tool_id"] == "draft_document"
    assert "name" not in record
    assert "phone" not in record
    assert "address" not in record
    assert "prompt" not in record
    assert "evidence" not in record


def test_confirmation_state_is_recorded_without_private_payload():
    event = make_agent_audit_event(
        capability_id="submission",
        tool_id="submit_external",
        decision=AgentDecision.CONFIRMATION_REQUIRED,
        risk="CONSEQUENTIAL",
        reason="explicit user confirmation required",
        confirmation_required=True,
        confirmation_obtained=False,
    )
    record = event.to_record()
    assert record["confirmation_required"] is True
    assert record["confirmation_obtained"] is False
    assert "case_data" not in record
