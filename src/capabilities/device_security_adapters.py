"""Platform adapter boundary for the device-security capability.

Adapters provide observations; they do not decide that a device is compromised.
The canonical evidence model in ``device_security`` remains authoritative.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from .device_security import DeviceSecurityReport, SecurityEvidence, SecurityObservation, build_report


@dataclass(frozen=True)
class AdapterContext:
    platform: str
    version: str | None = None


class DeviceSecurityAdapter(ABC):
    """Provider-neutral interface implemented by platform-specific adapters."""

    name: str

    @abstractmethod
    def collect_observations(self, context: AdapterContext) -> tuple[SecurityObservation, ...]:
        """Collect observations without upgrading their evidence strength."""
        raise NotImplementedError

    def audit(self, context: AdapterContext) -> DeviceSecurityReport:
        return build_report(self.collect_observations(context))


class UnavailableDeviceSecurityAdapter(DeviceSecurityAdapter):
    """Explicit adapter for platforms where no security probe is implemented."""

    name = "unavailable"

    def collect_observations(self, context: AdapterContext) -> tuple[SecurityObservation, ...]:
        return (
            SecurityObservation(
                code=f"PLATFORM_SECURITY_PROBES_UNAVAILABLE:{context.platform}",
                evidence=SecurityEvidence.UNAVAILABLE,
                detail="No platform-specific security adapter is currently implemented.",
            ),
        )
