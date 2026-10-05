"""Provider-neutral AI contract for optional Janavani model capabilities.

The contract carries purpose and data-scope metadata so provider adapters cannot
silently become capability owners. Providers generate; they do not authorize,
verify legal authority, or define Janavani truth.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Protocol

from src.access.capability_scope import CapabilityDataScope, CapabilityDataScopePolicy


@dataclass(frozen=True)
class AIRequest:
    purpose: str
    messages: tuple[Mapping[str, str], ...]
    model: str
    data_scope: tuple[str, ...] = field(default_factory=tuple)
    provenance_refs: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class AIResponse:
    provider_id: str
    model: str
    payload: Mapping[str, Any]


class AIProvider(Protocol):
    provider_id: str

    def generate(self, request: AIRequest) -> AIResponse:
        """Generate only the requested task output; no authorization semantics."""
        ...


class ScopedAIProvider(Protocol):
    provider_id: str

    def generate_scoped(
        self,
        request: AIRequest,
        *,
        scope_policy: CapabilityDataScopePolicy,
        consent_scope: CapabilityDataScope | None = None,
    ) -> AIResponse:
        """Generate only after the capability data scope permits execution."""
        ...
