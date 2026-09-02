"""Provider-neutral identity adapter boundary.

Adapters translate channel-specific authentication results into Janavani's
canonical identity context. Authentication and authorization remain separate.
"""

from typing import Protocol

from .context import IdentityContext
from .external import ExternalIdentity
from .principal import AuthenticationMethod, IdentityMode, Principal


class IdentityAdapter(Protocol):
    """Resolve one provider identity into a canonical request context."""

    def resolve(self, identity: ExternalIdentity) -> IdentityContext:
        """Return a usable identity context or raise for invalid identity."""
        ...


class DefaultIdentityAdapter:
    """Provider-neutral adapter for already-verified external identities.

    Provider-specific token validation belongs outside this class. This class
    only enforces the shared boundary after an upstream provider has verified
    the external identity.
    """

    def resolve(self, identity: ExternalIdentity) -> IdentityContext:
        if not identity.is_usable():
            raise ValueError("external identity is inactive or unverified")

        try:
            method = AuthenticationMethod(identity.authentication_method)
        except ValueError as exc:
            raise ValueError("unsupported authentication method") from exc

        if method == AuthenticationMethod.NONE:
            raise ValueError("authenticated identity requires an authentication method")

        principal = Principal(
            principal_id=identity.principal_id,
            identity_mode=IdentityMode.AUTHENTICATED,
            interface=identity.provider,
            authentication_method=method,
        )
        return IdentityContext(principal=principal)
