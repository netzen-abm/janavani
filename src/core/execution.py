"""Provider- and surface-neutral execution context for shared capabilities."""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import Enum
from uuid import uuid4

from src.identity.context import IdentityContext


class SideEffectClass(str, Enum):
    READ = "read"
    LOCAL_MUTATION = "local_mutation"
    EXTERNAL_SIDE_EFFECT = "external_side_effect"


class TrustClass(str, Enum):
    CITIZEN_PROVIDED = "citizen_provided"
    AUTHORITATIVE = "authoritative"
    SYSTEM_DERIVED = "system_derived"
    EXPERT_REVIEWED = "expert_reviewed"
    AI_GENERATED = "ai_generated"
    UNVERIFIED = "unverified"


@dataclass(frozen=True)
class ProvenanceRecord:
    source_ref: str
    source_type: TrustClass
    publisher: str | None = None
    retrieved_at: str | None = None
    transformation: str | None = None
    provider_ref: str | None = None
    confidence: float | None = None
    verification_status: str = "UNVERIFIED"
    parent_refs: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if not self.source_ref.strip():
            raise ValueError("Provenance source_ref must not be blank")
        if self.confidence is not None and not 0.0 <= self.confidence <= 1.0:
            raise ValueError("Provenance confidence must be between 0 and 1")


@dataclass(frozen=True)
class CapabilityExecutionContext:
    identity: IdentityContext
    capability_id: str
    action: str
    surface: str
    resource_id: str | None = None
    operation_id: str = field(default_factory=lambda: f"op_{uuid4().hex}")
    correlation_id: str | None = None
    parent_operation_id: str | None = None
    idempotency_key: str | None = None
    authorization_ref: str | None = None
    consent_refs: tuple[str, ...] = field(default_factory=tuple)
    policy_ref: str | None = None
    risk_level: str = "normal"
    side_effect_class: SideEffectClass = SideEffectClass.READ
    provenance: tuple[ProvenanceRecord, ...] = field(default_factory=tuple)
    metadata: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.capability_id.strip() or not self.action.strip():
            raise ValueError("capability_id and action must not be blank")
        if not self.surface.strip() or not self.operation_id.strip():
            raise ValueError("surface and operation_id must not be blank")
        if self.risk_level not in {"low", "normal", "high", "critical"}:
            raise ValueError("invalid risk_level")
        if self.side_effect_class is SideEffectClass.EXTERNAL_SIDE_EFFECT and not self.idempotency_key:
            raise ValueError("External side effects require an idempotency_key")
        if self.correlation_id == "":
            raise ValueError("correlation_id must be non-blank when supplied")

    @classmethod
    def for_capability(
        cls,
        identity: IdentityContext,
        *,
        capability_id: str,
        action: str,
        surface: str,
        resource_id: str | None = None,
        correlation_id: str | None = None,
        parent_operation_id: str | None = None,
        idempotency_key: str | None = None,
        authorization_ref: str | None = None,
        consent_refs: tuple[str, ...] = (),
        policy_ref: str | None = None,
        risk_level: str = "normal",
        side_effect_class: SideEffectClass = SideEffectClass.READ,
        provenance: tuple[ProvenanceRecord, ...] = (),
        metadata: Mapping[str, str] | None = None,
    ) -> CapabilityExecutionContext:
        return cls(
            identity=identity,
            capability_id=capability_id,
            action=action,
            surface=surface,
            resource_id=resource_id,
            correlation_id=correlation_id or identity.request_id,
            parent_operation_id=parent_operation_id,
            idempotency_key=idempotency_key,
            authorization_ref=authorization_ref,
            consent_refs=consent_refs,
            policy_ref=policy_ref,
            risk_level=risk_level,
            side_effect_class=side_effect_class,
            provenance=provenance,
            metadata=metadata or {},
        )
