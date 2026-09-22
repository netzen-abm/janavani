"""Provider-neutral capability data-scope policy.

This boundary constrains which data fields a capability may request and binds
approved processing to the declared provider and processing mode. It does not
grant identity authorization or perform transmission; those remain separate
trust/provider boundaries.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import FrozenSet


class DataClassification(str, Enum):
    PUBLIC = "public"
    NON_SENSITIVE = "non_sensitive"
    PERSONAL = "personal"
    SENSITIVE = "sensitive"
    HIGH_RISK = "high_risk"


class CapabilityScopeDecision(str, Enum):
    ALLOW = "allow"
    REQUIRE_CONSENT = "require_consent"
    DENY = "deny"


@dataclass(frozen=True)
class DataRequirement:
    field: str
    classification: DataClassification
    required: bool = True


@dataclass(frozen=True)
class CapabilityDataScope:
    capability_id: str
    purpose: str
    approved_fields: FrozenSet[str]
    provider: str | None = None
    processing_mode: str | None = None

    def permits(
        self,
        *,
        capability_id: str,
        purpose: str,
        requested_fields: FrozenSet[str],
        provider: str | None,
        processing_mode: str | None,
    ) -> bool:
        return (
            capability_id == self.capability_id
            and purpose == self.purpose
            and provider == self.provider
            and processing_mode == self.processing_mode
            and requested_fields.issubset(self.approved_fields)
        )


@dataclass(frozen=True)
class CapabilityDataScopePolicy:
    capability_id: str
    requirements: tuple[DataRequirement, ...]
    consent_required_for: FrozenSet[DataClassification] = frozenset(
        {
            DataClassification.PERSONAL,
            DataClassification.SENSITIVE,
            DataClassification.HIGH_RISK,
        }
    )

    def requirement_map(self) -> dict[str, DataRequirement]:
        return {item.field: item for item in self.requirements}

    def evaluate(
        self,
        *,
        purpose: str,
        requested_fields: FrozenSet[str],
        provider: str | None,
        processing_mode: str | None,
        consent_scope: CapabilityDataScope | None = None,
    ) -> CapabilityScopeDecision:
        if self.capability_id.strip() == "" or not purpose.strip():
            return CapabilityScopeDecision.DENY

        requirements = self.requirement_map()
        if requested_fields - requirements.keys():
            return CapabilityScopeDecision.DENY

        needs_consent = any(
            requirements[field].classification in self.consent_required_for
            for field in requested_fields
        )
        if not needs_consent:
            return CapabilityScopeDecision.ALLOW

        if consent_scope is None:
            return CapabilityScopeDecision.REQUIRE_CONSENT

        return (
            CapabilityScopeDecision.ALLOW
            if consent_scope.permits(
                capability_id=self.capability_id,
                purpose=purpose,
                requested_fields=requested_fields,
                provider=provider,
                processing_mode=processing_mode,
            )
            else CapabilityScopeDecision.REQUIRE_CONSENT
        )
