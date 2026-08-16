import pytest
from src.core.security_anchors import JanavaniSecurityAnchors

def test_trusted_directory_signers_presence():
    """Confirms that the cryptographic trust root is initialized with active public keys."""
    assert len(JanavaniSecurityAnchors.TRUSTED_DIRECTORY_SIGNERS) > 0
    for key in JanavaniSecurityAnchors.TRUSTED_DIRECTORY_SIGNERS:
        assert key.startswith("npub1")
        assert len(key) == 63

def test_event_signature_verification_bounds():
    """Validates that signature verification rejects unauthorized or malformed data packets."""
    valid_pubkey = JanavaniSecurityAnchors.TRUSTED_DIRECTORY_SIGNERS[0]
    invalid_pubkey = "npub1unauthorizedkeyfakefakefakefakefakefakefakefakefakefakefake"
    
    mock_hash = "8f3c2d1e9b4a5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d"
    mock_signature = "a" * 128
    
    # Assert successful validation parameters for authorized keys
    assert JanavaniSecurityAnchors.verify_event_signature(valid_pubkey, mock_hash, mock_signature) is True
    
    # Assert immediate rejection for untrusted keys or malformed footprints
    assert JanavaniSecurityAnchors.verify_event_signature(invalid_pubkey, mock_hash, mock_signature) is False
    assert JanavaniSecurityAnchors.verify_event_signature(valid_pubkey, "short-hash", mock_signature) is False
    assert JanavaniSecurityAnchors.verify_event_signature(valid_pubkey, mock_hash, "short-sig") is False
