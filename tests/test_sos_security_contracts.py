from __future__ import annotations

from datetime import timedelta

import fakeredis

from src.core.sos import CredentialSessionRevocation, TransientDataDestruction
from src.identity.principal import AuthenticationMethod
from src.identity.session import SessionManager
from src.storage.cache import TransientStorageEngine


def test_transient_storage_implements_scoped_deletion_contract() -> None:
    engine = TransientStorageEngine()
    engine.redis_client = fakeredis.FakeRedis(decode_responses=True)
    engine.redis_client.set("transient_doc:sos-1", "sensitive")
    assert hasattr(TransientDataDestruction, "delete_transient_document")
    assert engine.delete_transient_document("sos-1") is True
    assert engine.redis_client.exists("transient_doc:sos-1") == 0


def test_session_manager_implements_revocation_contract() -> None:
    manager = SessionManager()
    assert hasattr(CredentialSessionRevocation, "revoke")
    assert hasattr(manager, "revoke")


def test_revocation_invalidates_session() -> None:
    manager = SessionManager(ttl=timedelta(minutes=5))
    token, record = manager.create_session(
        "citizen-1",
        authentication_method=AuthenticationMethod.PASSKEY,
    )
    manager.revoke(record.session_id)

    try:
        manager.resolve(record.session_id, token)
    except PermissionError:
        return
    raise AssertionError("revoked session remained usable")
