import pytest

from src.authorization.issuance import CapabilityGrantDenied, build_principal, issue_capability_grants
from src.authorization.capabilities import DOCUMENT_GENERATE
from src.identity.principal import AuthenticationMethod, IdentityMode


def test_unknown_grant_is_rejected_before_principal_creation():
    with pytest.raises(ValueError):
        issue_capability_grants(
            frozenset({"admin.delete_everything"}),
            identity_mode=IdentityMode.AUTHENTICATED,
            authentication_method=AuthenticationMethod.OIDC,
        )


def test_protected_grant_cannot_be_issued_to_anonymous_identity():
    with pytest.raises(CapabilityGrantDenied):
        issue_capability_grants(
            frozenset({DOCUMENT_GENERATE}),
            identity_mode=IdentityMode.ANONYMOUS,
            authentication_method=AuthenticationMethod.NONE,
        )


def test_protected_grant_requires_citizen_authentication_method():
    with pytest.raises(CapabilityGrantDenied):
        issue_capability_grants(
            frozenset({DOCUMENT_GENERATE}),
            identity_mode=IdentityMode.AUTHENTICATED,
            authentication_method=AuthenticationMethod.SERVICE_CREDENTIAL,
        )


def test_authenticated_principal_can_receive_registered_protected_grant():
    principal = build_principal(
        principal_id="opaque-user-1",
        interface="web",
        identity_mode=IdentityMode.AUTHENTICATED,
        authentication_method=AuthenticationMethod.OIDC,
        capabilities=frozenset({DOCUMENT_GENERATE}),
    )
    assert DOCUMENT_GENERATE in principal.capabilities
