from __future__ import annotations

from types import SimpleNamespace

from src.ai.provider import AIRequest
from src.ai.providers.ollama import OllamaProvider, OllamaSettings
from src.ai.providers.huggingface_translation import HuggingFaceTranslationProvider


class FakeResponse:
    def __init__(self, body):
        self._body = body

    def raise_for_status(self):
        return None

    def json(self):
        return self._body


class FakeClient:
    def __init__(self, body):
        self.body = body
        self.calls = []

    def post(self, url, **kwargs):
        self.calls.append((url, kwargs))
        return FakeResponse(self.body)


def test_ollama_implements_canonical_provider_contract():
    client = FakeClient({"message": {"role": "assistant", "content": "ok"}})
    provider = OllamaProvider(
        OllamaSettings(base_url="http://ollama", model="local-model"),
        client=client,
    )
    response = provider.generate(
        AIRequest(
            purpose="test",
            messages=({"role": "user", "content": "hello"},),
            model="local-model",
        )
    )
    assert response.provider_id == "ollama-local"
    assert response.model == "local-model"
    assert client.calls


def test_huggingface_translation_provider_returns_canonical_response(monkeypatch):
    monkeypatch.setattr(
        "src.ai.providers.huggingface_translation.ai_settings",
        SimpleNamespace(HF_TOKEN="token"),
    )
    client = FakeClient([{"translation_text": "namaste"}])
    provider = HuggingFaceTranslationProvider(client)
    response = provider.generate(
        AIRequest(
            purpose="civic_translation",
            messages=({"role": "user", "content": "hello"},),
            model="translation-model",
            data_scope=("citizen_text",),
        )
    )
    assert response.provider_id == "huggingface-translation"
    assert response.payload["translated_text"] == "namaste"
