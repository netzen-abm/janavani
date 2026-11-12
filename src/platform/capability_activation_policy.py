"""Platform-level activation policy for consequential capabilities.

This policy is an activation boundary, not a replacement for domain authorization,
consent, explicit approval, or execution-context validation.
"""
from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping

CAPABILITY_MATURITY = (
    "designed",
    "implemented",
    "composed",
    "integration_verified",
    "production_approved",
    "suspended",
    "retired",
)


@dataclass(frozen=True)
class CapabilityActivation:
    capability_id: str
    maturity: str
    enabled: bool = False
    allowed_surfaces: frozenset[str] = frozenset()
    allowed_environments: frozenset[str] = frozenset()
    dependencies_verified: bool = False
    accountable_owner: str | None = None
    approval_ref: str | None = None

    def __post_init__(self) -> None:
        if not self.capability_id.strip():
            raise ValueError("capability_id must not be blank")
        if self.maturity not in CAPABILITY_MATURITY:
            raise ValueError(f"Unsupported capability maturity: {self.maturity}")
        if any(not value.strip() for value in self.allowed_surfaces | self.allowed_environments):
            raise ValueError("Allowed surfaces and environments must not contain blank values")


@dataclass(frozen=True)
class CapabilityActivationPolicy:
    """Immutable, deny-by-default activation policy for one runtime composition."""

    environment: str
    surface: str
    activations: Mapping[str, CapabilityActivation]

    def __post_init__(self) -> None:
        if not self.environment.strip() or not self.surface.strip():
            raise ValueError("environment and surface must not be blank")
        snapshot = dict(self.activations)
        for key, activation in snapshot.items():
            if key != activation.capability_id:
                raise ValueError("Activation mapping key must match capability_id")
        object.__setattr__(self, "activations", MappingProxyType(snapshot))

    def permits(self, capability_id: str) -> bool:
        """Return True only when every platform activation condition is satisfied."""
        activation = self.activations.get(capability_id)
        if activation is None or not activation.enabled:
            return False
        if activation.maturity in {"suspended", "retired"}:
            return False
        required_maturity = (
            "production_approved" if self.environment == "production"
            else "integration_verified"
        )
        if CAPABILITY_MATURITY.index(activation.maturity) < CAPABILITY_MATURITY.index(required_maturity):
            return False
        if self.surface not in activation.allowed_surfaces:
            return False
        if self.environment not in activation.allowed_environments:
            return False
        if not activation.dependencies_verified:
            return False
        if not activation.accountable_owner or not activation.accountable_owner.strip():
            return False
        if not activation.approval_ref or not activation.approval_ref.strip():
            return False
        return True
