"""Canonical validation for capability grants.

Identity adapters may describe authentication, but they must not invent
arbitrary authority. Every capability grant must be registered explicitly.
"""

from typing import FrozenSet

from .capabilities import PROTECTED_CAPABILITIES, PUBLIC_CAPABILITIES

KNOWN_CAPABILITIES: FrozenSet[str] = frozenset(
    PUBLIC_CAPABILITIES | PROTECTED_CAPABILITIES
)


class InvalidCapabilityGrant(ValueError):
    """Raised when a requested capability is not registered."""


def validate_capability_grants(capabilities: FrozenSet[str]) -> FrozenSet[str]:
    """Return validated grants or reject unknown capability identifiers."""
    unknown = capabilities - KNOWN_CAPABILITIES
    if unknown:
        raise InvalidCapabilityGrant(
            "unknown capability grant(s): " + ", ".join(sorted(unknown))
        )
    return frozenset(capabilities)


def validate_protected_grants(capabilities: FrozenSet[str]) -> FrozenSet[str]:
    """Validate grants before a protected capability reaches a Principal."""
    validated = validate_capability_grants(capabilities)
    return frozenset(validated & PROTECTED_CAPABILITIES)
