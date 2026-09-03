import pytest

from src.authorization.consent import ConsentRequired
from src.authorization.transmission import (
    TRANSMIT_ACTION,
    TRANSMIT_CAPABILITY,
    authorize_transmission,
)
from src.identity.context import IdentityContext
from src.identity.principal import Principal


def context_with_transmit_capability() -> IdentityContext:
    principal = Principal(
        principal_id="user-1",
        capabilities=frozenset({TRANSMIT_CAPABILITY}),
    )
    return IdentityContext(principal=principal)


def test_transmission_requires_explicit_consent():
    with pytest.raises(ConsentRequired):
        authorize_transmission(
            context_with_transmit_capability(),
            "government-office",
        )


def test_authorized_transmission_requires_both_capability_and_consent():
    result = authorize_transmission(
        context_with_transmit_capability(),
        "government-office",
        granted_consent_actions=frozenset({TRANSMIT_ACTION}),
    )

    assert result.destination == "government-office"
    assert result.consent.consented is True


def test_anonymous_or_unprivileged_transmission_is_denied():
    context = IdentityContext(Principal(principal_id="anon-1"))
    with pytest.raises(PermissionError):
        authorize_transmission(
            context,
            "government-office",
            granted_consent_actions=frozenset({TRANSMIT_ACTION}),
        )
