from __future__ import annotations

from src.core.sos import CredentialSessionRevocation, TransientDataDestruction
from src.identity.session import SessionManager
from src.storage.cache import TransientStorageEngine


def test_transient_storage_exposes_scoped_deletion_contract() -> None:
    assert hasattr(TransientStorageEngine, "delete_transient_document")
    assert TransientDataDestruction


def test_session_manager_is_canonical_revocation_provider() -> None:
    manager = SessionManager()
    assert hasattr(manager, "revoke")
    assert CredentialSessionRevocation


def test_revocation_invalidates_session() -> None:
    from datetime import timedelta
    from src.identity.principal import AuthenticationMethod

    manager = SessionManager(ttl=timedelta(minutes=5))
    token, record = manager.create_session(
        "citizen-1",
        authentication_method=AuthenticationMethod.PASSWORD,
    )
    manager.revoke(record.session_id)

    try:
        manager.resolve(record.session_id, token)
    except PermissionError:
        return
    raise AssertionError("revoked session remained usable")
