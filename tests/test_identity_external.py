from src.identity.external import ExternalIdentity


def test_external_identity_requires_active_and_verified():
    identity = ExternalIdentity(
        provider="telegram",
        subject="example-subject",
        principal_id="janavani-user-1",
        authentication_method="service_credential",
        verified=True,
    )

    assert identity.is_active()
    assert identity.is_usable()


def test_revoked_identity_is_not_usable():
    identity = ExternalIdentity(
        provider="telegram",
        subject="example-subject",
        principal_id="janavani-user-1",
        authentication_method="service_credential",
        verified=True,
        revoked_at="2026-09-02T00:00:00Z",
    )

    assert not identity.is_active()
    assert not identity.is_usable()
