"""Capability-scoped consent and minimum-data policy evaluation.

This module is deliberately provider- and channel-neutral. It decides whether a
capability request is permitted; it does not transmit data or perform actions.
"""
from dataclasses import dataclass
from enum import Enum
from typing import FrozenSet, Mapping, Optional, Tuple


class DataClass(str, Enum):
    PUBLIC = "PUBLIC"
    NON_SENSITIVE = "NON_SENSITIVE"
    PERSONAL = "PERSONAL"
    SENSITIVE = "SENSITIVE"
    HIGH_RISK = "HIGH_RISK"


class ConsentDecision(str, Enum):
    ALLOW = "ALLOW"
    REQUIRE_CONSENT = "REQUIRE_CONSENT"
    DENY = "DENY"


@dataclass(frozen=True)
class DataRequirement:
    field: str
    classification: DataClass
    required: bool = True


@dataclass(frozen=True)
class ConsentRequest:
    capability_id: str
    purpose: str
    requested_data: Tuple[str, ...]
    provider: Optional[str] = None
    processing_mode: Optional[str] = None
    consequential_action: bool = False


@dataclass(frozen=True)
class ConsentScope:
    capability_id: str
    purpose: str
    approved_data: FrozenSet[str]
    provider: Optional[str] = None
    processing_mode: Optional[str] = None

    def permits(self, request: ConsentRequest) -> bool:
        return (
            request.capability_id == self.capability_id
            and request.purpose == self.purpose
            and request.provider == self.provider
            and request.processing_mode == self.processing_mode
            and set(request.requested_data).issubset(self.approved_data)
        )


@dataclass(frozen=True)
class CapabilityPolicy:
    capability_id: str
    requirements: Tuple[DataRequirement, ...]
    consent_required_for: FrozenSet[DataClass] = frozenset(
        {DataClass.PERSONAL, DataClass.SENSITIVE, DataClass.HIGH_RISK}
    )
    consequential_action_requires_consent: bool = True

    def requirement_map(self) -> Mapping[str, DataRequirement]:
        return {item.field: item for item in self.requirements}


def evaluate_consent(
    request: ConsentRequest,
    policy: CapabilityPolicy,
    scope: Optional[ConsentScope] = None,
) -> ConsentDecision:
    """Evaluate a capability request using minimum-data and scoped consent rules."""
    if request.capability_id != policy.capability_id or not request.purpose.strip():
        return ConsentDecision.DENY

    requirements = policy.requirement_map()
    if any(field not in requirements for field in request.requested_data):
        return ConsentDecision.DENY

    if request.consequential_action and policy.consequential_action_requires_consent:
        if scope is None or not scope.permits(request):
            return ConsentDecision.REQUIRE_CONSENT

    needs_consent = any(
        requirements[field].classification in policy.consent_required_for
        for field in request.requested_data
    )
    if not needs_consent:
        return ConsentDecision.ALLOW

    return ConsentDecision.ALLOW if scope is not None and scope.permits(request) else ConsentDecision.REQUIRE_CONSENT
