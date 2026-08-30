"""Shared data-classification and outbound-processing policy.

Fail-closed by default. Personal and sensitive information remains local unless
a future, explicit capability policy grants a narrowly scoped transmission.
This module contains no channel-specific or AI-specific logic.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Mapping


class DataClass(str, Enum):
    PUBLIC = "public"
    NON_SENSITIVE = "non_sensitive"
    PERSONAL = "personal"
    SENSITIVE = "sensitive"
    HIGH_RISK = "high_risk"


@dataclass(frozen=True)
class DataField:
    name: str
    value: Any
    classification: DataClass


@dataclass(frozen=True)
class PolicyDecision:
    allowed: bool
    fields: dict[str, Any]
    reason: str | None = None


class DataPolicy:
    """Reusable fail-closed policy engine for any outbound processing."""

    def classify(self, fields: Mapping[str, Any], classifications: Mapping[str, DataClass]) -> list[DataField]:
        return [
            DataField(name, value, classifications.get(name, DataClass.HIGH_RISK))
            for name, value in fields.items()
        ]

    def authorize(
        self,
        fields: Mapping[str, Any],
        classifications: Mapping[str, DataClass],
        *,
        user_authorized: bool = False,
        purpose: str | None = None,
    ) -> PolicyDecision:
        if not user_authorized:
            return PolicyDecision(False, {}, "explicit_user_authorization_required")
        if not purpose:
            return PolicyDecision(False, {}, "processing_purpose_required")

        classified = self.classify(fields, classifications)
        if any(item.classification in {DataClass.PERSONAL, DataClass.SENSITIVE, DataClass.HIGH_RISK} for item in classified):
            return PolicyDecision(False, {}, "private_or_sensitive_data_requires_stronger_policy")

        return PolicyDecision(True, {item.name: item.value for item in classified})

    def sanitize_public_context(
        self,
        fields: Mapping[str, Any],
        classifications: Mapping[str, DataClass],
    ) -> PolicyDecision:
        classified = self.classify(fields, classifications)
        if any(item.classification in {DataClass.PERSONAL, DataClass.SENSITIVE, DataClass.HIGH_RISK} for item in classified):
            return PolicyDecision(False, {}, "private_or_sensitive_data_rejected")
        return PolicyDecision(True, {item.name: item.value for item in classified})
