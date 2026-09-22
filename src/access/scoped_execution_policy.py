"""Provider-neutral scope gate for agentic and automated capability execution.

This policy is intentionally separate from identity and authorization. It constrains
what data, provider, processing mode, and purpose a capability execution may use.
""" 
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ScopedExecutionRequest:
    capability: str
    purpose: str
    requested_fields: frozenset[str]
    provider: str
    processing_mode: str


@dataclass(frozen=True)
class ScopedExecutionPolicy:
    capability: str
    allowed_fields: frozenset[str]
    allowed_providers: frozenset[str]
    allowed_processing_modes: frozenset[str]
    allowed_purposes: frozenset[str] = frozenset()

    def allows(self, request: ScopedExecutionRequest) -> bool:
        if request.capability != self.capability:
            return False
        if not request.purpose.strip():
            return False
        if request.requested_fields - self.allowed_fields:
            return False
        if request.provider not in self.allowed_providers:
            return False
        if request.processing_mode not in self.allowed_processing_modes:
            return False
        if self.allowed_purposes and request.purpose not in self.allowed_purposes:
            return False
        return True
