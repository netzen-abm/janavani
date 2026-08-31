import pytest

from src.authorization.capabilities import (
    DOCUMENT_GENERATE,
    DOCUMENT_TRANSMIT,
    PUBLIC_CAPABILITIES,
)
from src.authorization.grants import (
    InvalidCapabilityGrant,
    validate_capability_grants,
    validate_protected_grants,
)


def test_registered_public_capability_is_valid():
    grants = validate_capability_grants(frozenset({"public.search_office"}))
    assert grants == frozenset({"public.search_office"})


def test_unknown_capability_cannot_be_granted():
    with pytest.raises(InvalidCapabilityGrant):
        validate_capability_grants(frozenset({"admin.delete_everything"}))


def test_protected_capabilities_are_registered_but_not_public():
    assert DOCUMENT_GENERATE not in PUBLIC_CAPABILITIES
    assert DOCUMENT_TRANSMIT not in PUBLIC_CAPABILITIES
    assert DOCUMENT_GENERATE in validate_protected_grants(
        frozenset({DOCUMENT_GENERATE})
    )
