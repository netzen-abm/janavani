"""Issue validated capability grants to normalized principals.

Authentication proves identity; this boundary decides which registered
capabilities may actually be attached to that identity.
"""

from typing import FrozenSet

from src.identity.principal import AuthenticationMethod, IdentityMode, Principal

from .capabilities import PROTECTED_CAPABILITIES
from .grants import validate_capability_grants


class CapabilityGrantDenied(PermissionError):
    """Raised when a capability grant is not valid for the identity state."""


def issue_capability_grants(
    capabilities: FrozenSet[str],
    *,
    identity_mode: IdentityMode,
    authentication_method: AuthenticationMethod,
) -> FrozenSet[str]:
    """Validate and constrain grants before they become Principal authority."""
    validated = validate_capability_grants(capabilities)

    if PROTECTED_CAPABILITIES.intersection(validated):
        if identity_mode not in {
            IdentityMode.AUTHENTICATED,
            IdentityMode.CRYPTOGRAPHIC,
        }:
            raise CapabilityGrantDenied(
                "protected capabilities require authenticated or cryptographic identity"
            )
        if authentication_method in {
            AuthenticationMethod.NONE,
            AuthenticationMethod.SERVICE_CREDENTIAL,
        }:
            raise CapabilityGrantDenied(
                "protected capabilities require a citizen authentication method"
            )

    return validated


def build_principal(
    *,
    principal_id: str,
    interface: str,
    identity_mode: IdentityMode,
    authentication_method: AuthenticationMethod,
    capabilities: FrozenSet[str] = frozenset(),
    session_id: str | None = None,
) -> Principal:
    """Construct a Principal only after capability grants pass issuance policy."""
    validated = issue_capability_grants(
        capabilities,
        identity_mode=identity_mode,
        authentication_method=authentication_method,
    )
    return Principal(
        principal_id=principal_id,
        interface=interface,
        identity_mode=identity_mode,
        authentication_method=authentication_method,
        session_id=session_id,
        capabilities=validated,
    )
