"""Shared AI capability boundary for Janavani.

AI is a core ecosystem capability. Invocation is controlled by the citizen.
This contract deliberately accepts only sanitized context. Access surfaces and
providers must not bypass the privacy boundary by sending raw personal or
sensitive Case/Evidence data.
"""

from dataclasses import dataclass, field
from typing import Any, Protocol


@dataclass(frozen=True)
class SanitizedAIContext:
    task: str
    context: dict[str, Any] = field(default_factory=dict)
    language: str = "en"


@dataclass(frozen=True)
class AIRequest:
    context: SanitizedAIContext
    user_opted_in: bool
    requested_action: str


@dataclass(frozen=True)
class AIResult:
    ok: bool
    output: str | None = None
    provider: str | None = None
    error_code: str | None = None


class AIProvider(Protocol):
    name: str

    def run(self, request: AIRequest) -> AIResult: ...


class SharedAICapability:
    """Shared AI facade; the user controls invocation, providers are replaceable."""

    def __init__(self, providers: dict[str, AIProvider] | None = None):
        self._providers = providers or {}

    def register(self, provider: AIProvider) -> None:
        self._providers[provider.name] = provider

    def run(self, request: AIRequest, provider: str | None = None) -> AIResult:
        if not request.user_opted_in:
            return AIResult(ok=False, error_code="ai_not_enabled_by_user")
        if not self._providers:
            return AIResult(ok=False, error_code="no_ai_provider")
        selected = self._providers.get(provider) if provider else next(iter(self._providers.values()))
        if selected is None:
            return AIResult(ok=False, error_code="unknown_ai_provider")
        return selected.run(request)
