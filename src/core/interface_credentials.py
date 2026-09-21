"""Runtime-only interface credentials for service-to-service calls."""

import os
from dataclasses import dataclass


class CredentialConfigurationError(RuntimeError):
    """Raised when a required interface credential is not configured."""


@dataclass(frozen=True)
class InterfaceCredential:
    """A service credential used only at an interface-to-service boundary."""

    name: str
    value: str


def get_interface_credential(name: str) -> InterfaceCredential:
    """Load a required interface credential from the runtime environment."""
    value = os.getenv(name)
    if not value:
        raise CredentialConfigurationError(
            f"Required interface credential '{name}' is not configured"
        )
    return InterfaceCredential(name=name, value=value)
