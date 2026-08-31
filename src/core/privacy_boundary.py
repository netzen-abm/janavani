"""Capability-scoped privacy boundary.

This module is a policy boundary, not a PII detector or a substitute for
client-side data minimisation. Personal and sensitive citizen data remains
under user-device control; only explicitly permitted, minimised non-personal
payloads may cross a capability boundary.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Mapping


class DataClass(str, Enum):
    PUBLIC = "public"
    OPERATIONAL = "operational"
    USER_PRIVATE = "user_private"
    SENSITIVE = "sensitive"


class PrivacyBoundaryError(ValueError):
    """Raised when a payload violates the privacy boundary."""


@dataclass(frozen=True)
class CapabilityRequest:
    capability: str
    data_class: DataClass
    user_authorized: bool = False
    consent_granted: bool = False


# Defense-in-depth only. This is deliberately conservative and must never be
# treated as the primary privacy control; callers must use allow-listed,
# minimised fields before invoking this boundary.
_SENSITIVE_KEYS = frozenset(
    {
        "aadhaar",
        "address",
        "bank_account",
        "biometric",
        "dob",
        "email",
        "full_name",
        "phone",
        "phone_number",
        "pan",
        "password",
    }
)


def _contains_sensitive_key(value: Any) -> bool:
    """Return whether a mapping contains a known sensitive field name."""
    if isinstance(value, Mapping):
        for key, child in value.items():
            if str(key).strip().lower() in _SENSITIVE_KEYS:
                return True
            if _contains_sensitive_key(child):
                return True
    elif isinstance(value, (list, tuple)):
        return any(_contains_sensitive_key(item) for item in value)
    return False


def authorize_capability(request: CapabilityRequest, payload: Mapping[str, Any]) -> None:
    """Enforce the shared privacy/authorization boundary.

    USER_PRIVATE and SENSITIVE data never cross this boundary. Other data
    requires explicit user authorization, and consequential capabilities also
    require explicit consent.
    """
    if request.data_class in {DataClass.USER_PRIVATE, DataClass.SENSITIVE}:
        raise PrivacyBoundaryError(
            "Personal or sensitive data must remain under user-device control."
        )

    if not request.user_authorized:
        raise PrivacyBoundaryError("Capability use requires user authorization.")

    if not request.consent_granted:
        raise PrivacyBoundaryError("Explicit consent is required for this capability.")

    if _contains_sensitive_key(payload):
        raise PrivacyBoundaryError(
            "Payload contains a prohibited personal or sensitive field."
        )
