"""Capability-scoped consent and minimum-data policy primitives.

Consent is never a global permission. A grant is bound to a capability,
purpose, data scope, destination/provider and processing mode. Capabilities
must request the minimum data they need, and a grant cannot expand that scope.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import FrozenSet, Iterable, Optional


class DataClass(str, Enum):
    PUBLIC = "PUBLIC"
    NON_SENSITIVE = "NON_SENSITIVE"
    PERSONAL = "PERSONAL"
    SENSITIVE = "SENSITIVE"
    HIGH_RISK = "HIGH_RISK"


class ProcessingMode(str, Enum):
    LOCAL = "LOCAL"
    REMOTE = "REMOTE"
    HYBRID = "HYBRID"


class ConsentDecision(str, Enum):
    NOT_REQUIRED = "NOT_REQUIRED"
    REQUIRED = "REQUIRED"
    GRANTED = "GRANTED"
    DENIED = "DENIED"
    EXPIRED = "EXPIRED"
    SCOPE_MISMATCH = "SCOPE_MISMATCH"


@dataclass(frozen=True)
class DataRequirement:
    field: str
    classification: DataClass
    required: bool = True
    reason: str = ""


@dataclass(frozen=True)
class CapabilityPolicy:
    capability_id: str
    purpose: str
    requirements: tuple[DataRequirement, ...] = ()
    provider_id: Optional[str] = None
    processing_mode: ProcessingMode = ProcessingMode.LOCAL
    consent_required: bool = False
    consequential: bool = False

    @classmethod
    def create(
        cls,
        capability_id: str,
        purpose: str,
        requirements: Iterable[DataRequirement] = (),
        *,
        provider_id: Optional[str] = None,
        processing_mode: ProcessingMode = ProcessingMode.LOCAL,
        consent_required: bool = False,
        consequential: bool = False,
    ) -> "CapabilityPolicy":
        if not capability_id.strip() or not purpose.strip():
            raise ValueError("capability_id and purpose are required")
        return cls(
            capability_id=capability_id,
            purpose=purpose,
            requirements=tuple(requirements),
            provider_id=provider_id,
            processing_mode=processing_mode,
            consent_required=consent_required,
            consequential=consequential,
        )

    @property
    def required_fields(self) -> FrozenSet[str]:
        return frozenset(r.field for r in self.requirements if r.required)


@dataclass(frozen=True)
class ConsentGrant:
    capability_id: str
    purpose: str
    approved_fields: FrozenSet[str] = field(default_factory=frozenset)
    provider_id: Optional[str] = None
    processing_mode: ProcessingMode = ProcessingMode.LOCAL
    granted_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: Optional[datetime] = None
    grant_id: str = ""

    def is_expired(self, now: Optional[datetime] = None) -> bool:
        if self.expires_at is None:
            return False
        current = now or datetime.now(timezone.utc)
        return current >= self.expires_at


@dataclass(frozen=True)
class ConsentEvaluation:
    decision: ConsentDecision
    allowed_fields: FrozenSet[str] = field(default_factory=frozenset)
    missing_fields: FrozenSet[str] = field(default_factory=frozenset)
    reason: str = ""


class CapabilityConsentEvaluator:
    """Fail-closed evaluator for capability-scoped processing consent."""

    def evaluate(
        self,
        policy: CapabilityPolicy,
        grant: Optional[ConsentGrant],
        *,
        now: Optional[datetime] = None,
    ) -> ConsentEvaluation:
        required = policy.required_fields

        if not policy.consent_required:
            return ConsentEvaluation(
                decision=ConsentDecision.NOT_REQUIRED,
                allowed_fields=required,
                reason="Capability policy does not require user consent.",
            )

        if grant is None:
            return ConsentEvaluation(
                decision=ConsentDecision.REQUIRED,
                missing_fields=required,
                reason="Explicit consent for this capability scope is required.",
            )

        if grant.is_expired(now):
            return ConsentEvaluation(
                decision=ConsentDecision.EXPIRED,
                missing_fields=required,
                reason="The capability-scoped consent grant has expired.",
            )

        if grant.capability_id != policy.capability_id:
            return ConsentEvaluation(
                decision=ConsentDecision.SCOPE_MISMATCH,
                missing_fields=required,
                reason="Consent is bound to a different capability.",
            )

        if grant.purpose != policy.purpose:
            return ConsentEvaluation(
                decision=ConsentDecision.SCOPE_MISMATCH,
                missing_fields=required,
                reason="Consent is bound to a different processing purpose.",
            )

        if grant.provider_id != policy.provider_id:
            return ConsentEvaluation(
                decision=ConsentDecision.SCOPE_MISMATCH,
                missing_fields=required,
                reason="Consent is bound to a different provider.",
            )

        if grant.processing_mode != policy.processing_mode:
            return ConsentEvaluation(
                decision=ConsentDecision.SCOPE_MISMATCH,
                missing_fields=required,
                reason="Consent is bound to a different processing mode.",
            )

        missing = required - grant.approved_fields
        if missing:
            return ConsentEvaluation(
                decision=ConsentDecision.DENIED,
                allowed_fields=required - missing,
                missing_fields=missing,
                reason="The grant does not cover every required data field.",
            )

        return ConsentEvaluation(
            decision=ConsentDecision.GRANTED,
            allowed_fields=required,
            reason="Capability scope matches the explicit consent grant.",
        )


def require_consent(
    policy: CapabilityPolicy,
    grant: Optional[ConsentGrant],
    *,
    now: Optional[datetime] = None,
) -> ConsentEvaluation:
    """Evaluate a request without widening the policy's minimum-data scope."""
    return CapabilityConsentEvaluator().evaluate(policy, grant, now=now)
