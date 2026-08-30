"""Provider-neutral Agentic AI capability contract.

Agents can reason and prepare work, but tool use is scoped and consequential
external actions require explicit confirmation. All outbound context must pass
the shared PrivacyGateway first.
"""

from dataclasses import dataclass, field
from typing import Any, Protocol

from .privacy_gateway import PrivacyGateway


@dataclass(frozen=True)
class AgentRequest:
    task: str
    context: dict[str, Any]
    user_opted_in: bool
    allowed_tools: frozenset[str] = field(default_factory=frozenset)
    require_confirmation: bool = True


@dataclass(frozen=True)
class AgentResult:
    ok: bool
    output: str | None = None
    provider: str | None = None
    action_requires_confirmation: bool = False
    error_code: str | None = None


class AgentProvider(Protocol):
    name: str

    def run(self, request: AgentRequest) -> AgentResult: ...


class SharedAgenticAICapability:
    """Shared, provider-neutral agent facade with fail-closed privacy gating."""

    def __init__(self, privacy_gateway: PrivacyGateway, providers: dict[str, AgentProvider] | None = None):
        self._privacy_gateway = privacy_gateway
        self._providers = providers or {}

    def register(self, provider: AgentProvider) -> None:
        self._providers[provider.name] = provider

    def run(self, request: AgentRequest, provider: str | None = None) -> AgentResult:
        if not request.user_opted_in:
            return AgentResult(ok=False, error_code="agent_not_enabled_by_user")
        if not self._providers:
            return AgentResult(ok=False, error_code="no_agent_provider")

        decision = self._privacy_gateway.authorize_ai(request.context, request.user_opted_in)
        if not decision.allowed:
            return AgentResult(ok=False, error_code=decision.reason)

        selected = self._providers.get(provider) if provider else next(iter(self._providers.values()))
        if selected is None:
            return AgentResult(ok=False, error_code="unknown_agent_provider")

        scoped_request = AgentRequest(
            task=request.task,
            context=decision.context,
            user_opted_in=True,
            allowed_tools=request.allowed_tools,
            require_confirmation=request.require_confirmation,
        )
        return selected.run(scoped_request)
