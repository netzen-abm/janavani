from src.capabilities.responsibility import ResponsibilityCapability, ResponsibilityResolutionRequest
from src.core.authority import AuthorityContact, AuthorityRecord
from src.core.responsibility import ResolutionConfidence, ResponsibilityObservation
from src.storage.repositories.authority import InMemoryAuthorityRepository
from src.storage.repositories.responsibility import AuthorityBackedResponsibilityResolver


def observation(**overrides):
    values = {
        "observation_id": "obs-1",
        "description": "Road surface damage observed",
        "location": {"city": "Bengaluru"},
        "authority_type_hint": "Road authority",
    }
    values.update(overrides)
    return ResponsibilityObservation(**values)


def authority(*, verified: bool = True, source_refs=("official:road-record-1",)):
    return AuthorityRecord(
        authority_id="authority-1",
        name="Road Authority",
        authority_type="Road authority",
        jurisdiction={"city": "Bengaluru"},
        primary_contact=AuthorityContact(name="Road Desk", source_ref="official:contact-1", verified=verified),
        source_refs=source_refs,
        verification_status="VERIFIED" if verified else "UNVERIFIED",
    )


def test_authority_backed_resolver_returns_traceable_verified_match():
    repository = InMemoryAuthorityRepository([authority()])
    capability = ResponsibilityCapability(AuthorityBackedResponsibilityResolver(repository))

    resolution = capability.resolve(ResponsibilityResolutionRequest(observation()))

    assert resolution.observation_id == "obs-1"
    assert len(resolution.links) == 1
    link = resolution.links[0]
    assert link.confidence is ResolutionConfidence.MATCHED_RECORD
    assert link.verification_required is False
    assert link.source_refs == ("official:road-record-1",)
    assert resolution.has_verified_responsibility is True


def test_unverified_authority_remains_verification_required():
    repository = InMemoryAuthorityRepository([authority(verified=False)])
    capability = ResponsibilityCapability(AuthorityBackedResponsibilityResolver(repository))

    resolution = capability.resolve(ResponsibilityResolutionRequest(observation()))

    link = resolution.links[0]
    assert link.confidence is ResolutionConfidence.HIGH_CONFIDENCE
    assert link.verification_required is True
    assert resolution.has_verified_responsibility is False


def test_resolver_fails_closed_without_traceable_source():
    repository = InMemoryAuthorityRepository([authority(source_refs=())])
    capability = ResponsibilityCapability(AuthorityBackedResponsibilityResolver(repository))

    try:
        capability.resolve(ResponsibilityResolutionRequest(observation()))
    except ValueError as exc:
        assert "traceable source" in str(exc)
    else:
        raise AssertionError("Expected traceable-source validation failure")


def test_resolver_requires_explicit_jurisdiction_and_authority_hint():
    repository = InMemoryAuthorityRepository([authority()])
    resolver = AuthorityBackedResponsibilityResolver(repository)

    try:
        resolver.resolve(observation(location={}))
    except ValueError as exc:
        assert "city" in str(exc)
    else:
        raise AssertionError("Expected city validation failure")

    try:
        resolver.resolve(observation(authority_type_hint=None))
    except ValueError as exc:
        assert "authority type hint" in str(exc)
    else:
        raise AssertionError("Expected authority-type validation failure")
