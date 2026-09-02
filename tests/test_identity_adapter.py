import pytest

from src.identity.adapter import DefaultIdentityAdapter
from src.identity.external import ExternalIdentity
from src.identity.principal import AuthenticationMethod, IdentityMode


def test_verified_identity_maps_to_authenticated_principal():
    identity = ExternalIdentity(
        provider="telegram",
        subject="provider-subject-1",
        principal_id="principal-1",
        authentication_method=AuthenticationMethod.VERIFIED_PHONE.value,
        verified=True,
    )

    context = DefaultIdentityAdapter().resolve(identity)

    assert context.principal.principal_id == "principal-1"
    assert context.principal.identity_mode == IdentityMode.AUTHENTICATED
    assert context.principal.authentication_method == AuthenticationMethod.VERIFIED_PHONE
    assert context.principal.interface == "telegram"
    assert context.principal.principal_id != identity.subject


def test_unverified_identity_is_rejected():
    identity = ExternalIdentity(
        provider="oidc",
        subject="subject-1",
        principal_id="principal-1",
        authentication_method=AuthenticationMethod.OIDC.value,
        verified=False,
    )

    with pytest.raises(ValueError, match="inactive or unverified"):
        DefaultIdentityAdapter().resolve(identity)


def test_revoked_identity_is_rejected():
    identity = ExternalIdentity(
        provider="oidc",
        subject="subject-1",
        principal_id="principal-1",
        authentication_method=AuthenticationMethod.OIDC.value,
        verified=True,
        revoked_at="2026-09-02T00:00:00+00:00",
    )

    with pytest.raises(ValueError, match="inactive or unverified"):
        DefaultIdentityAdapter().resolve(identity)


def test_unsupported_authentication_method_is_rejected():
    identity = ExternalIdentity(
        provider="unknown",
        subject="subject-1",
        principal_id="principal-1",
        authentication_method="unsupported",
        verified=True,
    )

    with pytest.raises(ValueError, match="unsupported authentication method"):
        DefaultIdentityAdapter().resolve(identity)


def test_none_authentication_method_is_rejected():
    identity = ExternalIdentity(
        provider="local",
        subject="subject-1",
        principal_id="principal-1",
        authentication_method=AuthenticationMethod.NONE.value,
        verified=True,
    )

    with pytest.raises(ValueError, match="authenticated identity requires"):
        DefaultIdentityAdapter().resolve(identity)
