import pytest

from src.authorization.capabilities import DOCUMENT_GENERATE, PUBLIC_CAPABILITIES
from src.authorization.endpoint import AuthorizationDenied, authorize_capability
from src.authorization.policy import AuthorizationPolicy
from src.identity.context import anonymous_context
from src.identity.principal import AuthenticationMethod, IdentityMode, Principal


def test_anonymous_public_capability_is_allowed():
    context = anonymous_context("anon-1", interface="telegram")
    authorize_capability(
        context,
        DOCUMENT_GENERATE,
        policy=AuthorizationPolicy(anonymous_capabilities=PUBLIC_CAPABILITIES),
    )


def test_unknown_capability_is_denied():
    context = anonymous_context("anon-1")
    with pytest.raises(AuthorizationDenied):
        authorize_capability(
            context,
            "unknown.capability",
            policy=AuthorizationPolicy(anonymous_capabilities=PUBLIC_CAPABILITIES),
        )


def test_protected_capability_requires_grant():
    context = anonymous_context("anon-1")
    with pytest.raises(AuthorizationDenied):
        authorize_capability(
            context,
            "citizen.document.transmit",
            policy=AuthorizationPolicy(anonymous_capabilities=PUBLIC_CAPABILITIES),
        )


def test_authenticated_principal_uses_explicit_capability_grant():
    principal = Principal(
        principal_id="user-1",
        identity_mode=IdentityMode.AUTHENTICATED,
        authentication_method=AuthenticationMethod.OIDC,
        capabilities=frozenset({"citizen.document.transmit"}),
    )
    from src.identity.context import IdentityContext

    authorize_capability(
        IdentityContext(principal),
        "citizen.document.transmit",
        policy=AuthorizationPolicy(),
    )
