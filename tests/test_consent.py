import pytest

from src.authorization.consent import ConsentRequired, require_consent
from src.identity.context import IdentityContext
from src.identity.principal import Principal


def test_consent_is_required_by_default():
    context = IdentityContext(Principal("user-1"))

    with pytest.raises(ConsentRequired):
        require_consent(context, "document.transmit")


def test_explicit_consent_is_recorded():
    context = IdentityContext(Principal("user-1"))

    record = require_consent(
        context,
        "document.transmit",
        consented_actions=frozenset({"document.transmit"}),
    )

    assert record.principal_id == "user-1"
    assert record.action == "document.transmit"
    assert record.consented is True
    assert record.consented_at is not None
