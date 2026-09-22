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



def test_legal_agent_translation_fails_open(monkeypatch):
    """Translation provider failure must preserve the original citizen text."""
    from src.core.settings import ai_settings

    monkeypatch.setattr(ai_settings, "HF_TOKEN", "test-token")

    class FailingResponse:
        status_code = 503

    class FakeSession:
        def post(self, *args, **kwargs):
            return FailingResponse()

    agent = JanavaniLegalAgent(http_session=FakeSession())
    original = "റോഡ് തകർന്നിരിക്കുന്നു"
    assert agent.translate_input_if_needed(original) == original


def test_legal_agent_translation_uses_canonical_hf_token(monkeypatch):
    """Translation must use the injected session and canonical HF_TOKEN setting."""
    from src.core.settings import ai_settings

    monkeypatch.setattr(ai_settings, "HF_TOKEN", "test-token")
    monkeypatch.setattr(ai_settings, "IIT_MADRAS_TRANSLATION_MODEL", "test/model")

    class Response:
        status_code = 200

        def json(self):
            return [{"generated_text": "Road is damaged"}]

    class FakeSession:
        def __init__(self):
            self.calls = []

        def post(self, *args, **kwargs):
            self.calls.append((args, kwargs))
            return Response()

    session = FakeSession()
    result = JanavaniLegalAgent(http_session=session).translate_input_if_needed("റോഡ് തകർന്നിരിക്കുന്നു")

    assert result == "Road is damaged"
    assert session.calls
    assert "api-inference.huggingface.co/models/test/model" in session.calls[0][0][0]
    assert session.calls[0][1]["headers"]["Authorization"] == "Bearer test-token"


def test_legal_agent_regional_context_is_metadata_not_authority(monkeypatch):
    """Regional context must be bounded context and remain explicit in the result."""
    from src.core.settings import ai_settings

    monkeypatch.setattr(ai_settings, "OPENROUTER_API_KEY", "test-key")
    monkeypatch.setattr(ai_settings, "LEGAL_DRAFTING_MODEL", "test-model")

    class Response:
        def raise_for_status(self):
            return None

        def json(self):
            return {"choices": [{"message": {"content": "{}"}}]}

    class FakeSession:
        def __init__(self):
            self.calls = []

        def post(self, *args, **kwargs):
            self.calls.append((args, kwargs))
            return Response()

    session = FakeSession()
    result = JanavaniLegalAgent(http_session=session).draft_legal_document(
        "Roads in my area are damaged.", "KA-BLR-02"
    )

    assert result["status"] == "available"
    assert result["regional_profile"]["state"] == "Karnataka"
    prompt = session.calls[0][1]["json"]["messages"][0]["content"]
    assert "contextual routing metadata" in prompt
    assert "verified legal authority" in prompt
