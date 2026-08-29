"""Provider-neutral AI and Agentic AI capability boundary.

AI and agents are plug-in capabilities. No client or domain service should
hard-code a model/provider or depend on an agent being available.
"""
from __future__ import annotations
from typing import Any, Protocol
from pydantic import BaseModel, Field


class AIRequest(BaseModel):
    task: str = Field(min_length=2, max_length=200)
    input: str = Field(min_length=1, max_length=100000)
    context: dict[str, Any] = Field(default_factory=dict)
    mode: str = "auto"
    allow_external_processing: bool = False


class AIResult(BaseModel):
    ok: bool
    output: str | None = None
    provider: str | None = None
    model: str | None = None
    degraded: bool = False
    provenance: list[dict[str, Any]] = Field(default_factory=list)
    error_code: str | None = None


class AIProvider(Protocol):
    name: str
    def supports(self, request: AIRequest) -> bool: ...
    def execute(self, request: AIRequest) -> AIResult: ...


class AgentRequest(BaseModel):
    task: str = Field(min_length=2, max_length=200)
    input: str = Field(min_length=1, max_length=100000)
    tools: list[str] = Field(default_factory=list)
    require_confirmation: bool = True
    permissions: list[str] = Field(default_factory=list)


class AgentResult(BaseModel):
    ok: bool
    status: str
    output: str | None = None
    agent: str | None = None
    actions: list[dict[str, Any]] = Field(default_factory=list)
    requires_confirmation: bool = False
    audit_ref: str | None = None
    error_code: str | None = None


class AgentProvider(Protocol):
    name: str
    def supports(self, request: AgentRequest) -> bool: ...
    def execute(self, request: AgentRequest) -> AgentResult: ...


class AICapabilityRouter:
    """Selects an available provider without exposing provider identity to clients."""
    def __init__(self, providers: list[AIProvider] | None = None) -> None:
        self._providers = providers or []

    def register(self, provider: AIProvider) -> None:
        self._providers.append(provider)

    def execute(self, request: AIRequest) -> AIResult:
        for provider in self._providers:
            if provider.supports(request):
                return provider.execute(request)
        return AIResult(ok=False, degraded=True, error_code="ai_provider_unavailable")


class AgentCapabilityRouter:
    """Selects agent providers while preserving explicit permission/approval gates."""
    def __init__(self, providers: list[AgentProvider] | None = None) -> None:
        self._providers = providers or []

    def register(self, provider: AgentProvider) -> None:
        self._providers.append(provider)

    def execute(self, request: AgentRequest) -> AgentResult:
        for provider in self._providers:
            if provider.supports(request):
                return provider.execute(request)
        return AgentResult(ok=False, status="unavailable", error_code="agent_provider_unavailable")
