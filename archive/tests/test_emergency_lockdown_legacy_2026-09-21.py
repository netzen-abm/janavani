import pytest
import fakeredis
from src.services.emergency_sos import JanavaniEmergencySOSEngine

@pytest.fixture
def mock_lockdown_redis():
    """Provides an isolated memory container mock to test emergency features safely."""
    engine = JanavaniEmergencySOSEngine()
    engine.redis_client = fakeredis.FakeRedis(decode_responses=True)
    return engine

def test_emergency_sos_wipe_and_token_revocation(mock_lockdown_redis):
    """Verifies that the emergency module completely wipes raw session caches and blacklists tokens."""
    test_session_id = "target-session-xyz-999"
    test_token = "telegram-mvp-token-xyz"
    
    # Pre-populate sample session data within the volatile grid framework
    mock_lockdown_redis.redis_client.set(f"transient_doc:{test_session_id}", "sensitive-citizen-grievance-text")
    
    # Trigger the emergency lockdown operation
    response = mock_lockdown_redis.trigger_crisis_lockdown(
        session_tracking_id=test_session_id,
        client_interface_token=test_token,
        emergency_coordinates="11.2345, 75.6789"
    )
    
    # Assert that all critical actions completed successfully
    assert response["status"] == "CRISIS_LOCKDOWN_COMPLETED"
    assert response["local_volatile_cache_purged"] is True
    assert response["interface_token_revoked"] is True
    assert response["nostr_distress_signal_dispatched"] is True
    
    # Assert that data traces have been verified as completely deleted
    assert mock_lockdown_redis.redis_client.exists(f"transient_doc:{test_session_id}") == 0
    assert mock_lockdown_redis.redis_client.exists(f"security:blacklisted_tokens:{test_token}") == 1
