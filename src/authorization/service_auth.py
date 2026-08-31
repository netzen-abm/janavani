"""Authenticate internal service calls without conflating them with citizens."""

import hmac

from src.core.interface_credentials import get_interface_credential
from src.identity.context import IdentityContext
from src.identity.principal import AuthenticationMethod, IdentityMode, Principal


def service_context(
    supplied_token: str | None,
    *,
    credential_name: str,
    interface: str,
    capabilities: frozenset[str],
) -> IdentityContext | None:
    """Resolve an internal service token into a bounded service Principal."""
    if not supplied_token:
        return None

    try:
        expected = get_interface_credential(credential_name).value
    except Exception:
        return None

    if not hmac.compare_digest(supplied_token, expected):
        return None

    principal = Principal(
        principal_id=f"service:{interface}",
        identity_mode=IdentityMode.AUTHENTICATED,
        interface=interface,
        authentication_method=AuthenticationMethod.SERVICE_CREDENTIAL,
        capabilities=capabilities,
    )
    return IdentityContext(principal=principal)
