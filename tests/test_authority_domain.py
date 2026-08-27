from src.domain.authority import Authority, AuthoritySource, AuthorityVerificationStatus


def test_authority_requires_name_and_type() -> None:
    for name, authority_type, message in [
        ("   ", "office", "authority name is required"),
        ("District Office", "   ", "authority type is required"),
    ]:
        try:
            Authority.create(name, authority_type)
        except ValueError as exc:
            assert str(exc) == message
        else:
            raise AssertionError("invalid authority should be rejected")


def test_verified_authority_requires_provenance() -> None:
    try:
        Authority.create(
            "District Office",
            "government_office",
            verification_status=AuthorityVerificationStatus.VERIFIED,
        )
    except ValueError as exc:
        assert str(exc) == "verified authority requires source references"
    else:
        raise AssertionError("verified authority without provenance should be rejected")


def test_authority_verification_preserves_identity_and_source() -> None:
    source = AuthoritySource(
        source_id="SRC-1",
        source_type="OFFICIAL",
        uri="https://example.gov.in/office",
    )
    authority = Authority.create(
        "District Office",
        "government_office",
        source_refs=[source],
    )

    verified = authority.verify()

    assert verified.authority_id == authority.authority_id
    assert verified.source_refs == (source,)
    assert verified.verification_status is AuthorityVerificationStatus.VERIFIED
    assert verified.last_verified_at is not None
