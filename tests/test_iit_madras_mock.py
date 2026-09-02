from src.services.legal_agent import JanavaniLegalAgent


def test_legal_agent_degrades_without_ai_credentials(monkeypatch):
    """AI remains optional and degrades truthfully when unavailable."""
    from src.core.settings import ai_settings

    monkeypatch.setattr(ai_settings, "OPENROUTER_API_KEY", "")
    agent = JanavaniLegalAgent()

    result = agent.draft_legal_document("Roads in my area are damaged.")

    assert result["status"] == "degraded"
    assert result["ai_used"] is False
    assert "Roads" in result["draft"]


def test_legal_agent_rejects_empty_issue():
    """Empty civic input must not invoke an AI provider."""
    result = JanavaniLegalAgent().draft_legal_document("   ")

    assert result["status"] == "invalid_input"
    assert result["ai_used"] is False
