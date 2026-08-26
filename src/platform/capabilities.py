"""Canonical capability composition root.

The registry is built once by the application composition root. Interfaces
consume the same registry instead of constructing independent capability
instances per request.
"""

from __future__ import annotations

from .registry import CapabilityRegistry
from src.capabilities.complaint import ComplaintCapability


def build_capability_registry() -> CapabilityRegistry:
    """Create the default registry for currently implemented capabilities."""
    registry = CapabilityRegistry()
    registry.register(ComplaintCapability())
    return registry
