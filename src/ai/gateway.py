"""Shared AI execution boundary.

AI providers are reached only after canonical identity, authorization, execution
scope, and data-scope checks. The gateway is an execution adapter, not a second
authorization authority.
"""
from __future__ import annotations

from dataclasses import dataclass

from src.access.authorization import AuthorizationDecision, AuthorizationRequest, authorize
from src.access.capability_scope import CapabilityDataScope, CapabilityDataScopePolicy, CapabilityScopeDecision
from src.access.scoped_execution_policy import ScopedExecutionPolicy, ScopedExecutionRequest
from src.ai.provider import AIProvider, AIRequest, AIResponse
from src.core.execution import CapabilityExecutionContext
from src.identity.context import IdentityContext


@dataclass(frozen=True)
class AIExecutionRequest:
    identity: IdentityContext
    execution_context: CapabilityExecutionContext
    request: AIRequest
    provider: str
    processing_mode: str


class AIExecutionGateway:
    """Mandatory trust boundary between shared capabilities and AI providers."""

    def __init__(
        self,
        *,
        provider: AIProvider,
        scoped_policy: ScopedExecutionPolicy,
        data_scope_policy: CapabilityDataScopePolicy,
    ) -> None:
        self._provider = provider
        self._scoped_policy = scoped_policy
        self._data_scope_policy = data_scope_policy

    def generate(
        self,
        execution: AIExecutionRequest,
        *,
        consent_scope: CapabilityDataScope | None = None,
    ) -> AIResponse:
        context = execution.execution_context
        if context.identity.principal.principal_id != execution.identity.principal.principal_id:
            raise PermissionError("AI execution identity does not match execution context")

        if context.capability_id != self._scoped_policy.capability:
            raise PermissionError("AI execution capability is outside policy scope")

        authorization = authorize(
            AuthorizationRequest(
                context=execution.identity,
                capability=context.capability_id,
                action=context.action,
                resource_id=context.resource_id,
                risk_level=context.risk_level,
                execution_context=context,
            )
        )
        if authorization is not AuthorizationDecision.ALLOW:
            raise PermissionError(f"AI execution not authorized: {authorization.value}")

        if not self._scoped_policy.allows(
            ScopedExecutionRequest(
                capability=context.capability_id,
                purpose=execution.request.purpose,
                requested_fields=frozenset(execution.request.data_scope),
                provider=execution.provider,
                processing_mode=execution.processing_mode,
            )
        ):
            raise PermissionError("AI execution is outside scoped execution policy")

        scope = self._data_scope_policy.evaluate(
            purpose=execution.request.purpose,
            requested_fields=frozenset(execution.request.data_scope),
            provider=execution.provider,
            processing_mode=execution.processing_mode,
            consent_scope=consent_scope,
        )
        if scope is not CapabilityScopeDecision.ALLOW:
            raise PermissionError(f"AI data scope is not permitted: {scope.value}")

        return self._provider.generate(execution.request)
