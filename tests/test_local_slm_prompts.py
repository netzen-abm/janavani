from src.services.legal_agent import JanavaniLegalAgent


def test_legal_agent_prompt_boundaries_are_present():
    """The active AI adapter must request source-grounded civic drafting."""
    agent = JanavaniLegalAgent()
    source = agent.draft_legal_document.__doc__ or ""

    assert "legal advice" in source.lower()
    assert "source" in source.lower()
    assert "reviewed" in source.lower()


def test_legal_agent_has_no_open_chat_contract():
    """The adapter exposes structured document drafting, not general chat."""
    agent = JanavaniLegalAgent()

    assert hasattr(agent, "draft_legal_document")
    assert not hasattr(agent, "chat")
