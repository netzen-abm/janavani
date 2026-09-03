from datetime import timedelta

import pytest

from src.auth.session import InvalidSession, SessionManager
from src.identity.principal import AuthenticationMethod


def test_session_token_resolves_to_authenticated_context():
    manager = SessionManager(ttl=timedelta(minutes=15))
    token, record = manager.create_session(
        "user-opaque",
        authentication_method=AuthenticationMethod.PASSKEY,
        capabilities=frozenset({"citizen.document.generate"}),
    )

    context = manager.resolve(record.session_id, token, interface="web")
    assert context.principal.is_authenticated()
    assert context.principal.principal_id == "user-opaque"
    assert context.principal.session_id == record.session_id
    assert context.principal.has_capability("citizen.document.generate")


def test_wrong_token_fails_closed():
    manager = SessionManager()
    token, record = manager.create_session(
        "user-opaque",
        authentication_method=AuthenticationMethod.PASSKEY,
    )

    with pytest.raises(InvalidSession):
        manager.resolve(record.session_id, token + "x")


def test_revoked_session_cannot_be_resolved():
    manager = SessionManager()
    token, record = manager.create_session(
        "user-opaque",
        authentication_method=AuthenticationMethod.PASSKEY,
    )
    manager.revoke(record.session_id)

    with pytest.raises(InvalidSession):
        manager.resolve(record.session_id, token)
