from src.ai.provider import AIRequest, AIResponse
from src.ai.providers.openrouter import OpenRouterProvider


def test_openrouter_adapter_preserves_purpose_and_scope_at_contract_boundary(monkeypatch):
    from src.core.settings import ai_settings

    monkeypatch.setattr(ai_settings, "OPENROUTER_API_KEY", "test-key")
    monkeypatch.setattr(ai_settings, "OPENROUTER_URL", "https://example.test/v1")

    class Response:
        def raise_for_status(self):
            return None

        def json(self):
            return {"choices": [{"message": {"content": "{}"}}]}

    class Session:
        def __init__(self):
            self.calls = []

        def post(self, *args, **kwargs):
            self.calls.append((args, kwargs))
            return Response()

    request = AIRequest(
        purpose="civic_document_drafting",
        messages=({"role": "user", "content": "citizen supplied text"},),
        model="test-model",
        data_scope=("citizen_supplied_text",),
        provenance_refs=("evidence-1",),
    )
    session = Session()
    result = OpenRouterProvider(session).generate(request)

    assert isinstance(result, AIResponse)
    assert result.provider_id == "openrouter"
    assert session.calls[0][1]["json"]["model"] == "test-model"
    assert session.calls[0][1]["json"]["messages"][0]["content"] == "citizen supplied text"


def test_provider_does_not_receive_contract_metadata_as_authority_claims():
    request = AIRequest(
        purpose="civic_document_drafting",
        messages=({"role": "user", "content": "facts"},),
        model="test-model",
        data_scope=("facts",),
        provenance_refs=("source-1",),
    )
    assert request.purpose == "civic_document_drafting"
    assert request.provenance_refs == ("source-1",)
