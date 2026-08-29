from src.platform.encrypted_envelope import EncryptedEnvelope, assert_opaque


def test_encrypted_envelope_is_opaque():
    envelope = EncryptedEnvelope(
        key_reference="device-key:case-1",
        nonce_b64="abcdefghijklmnop",
        ciphertext_b64="encrypted-citizen-data",
    )
    assert assert_opaque(envelope) is envelope
    assert envelope.ciphertext_b64 == "encrypted-citizen-data"


def test_envelope_rejects_unexpected_fields():
    try:
        EncryptedEnvelope(
            key_reference="device-key:case-1",
            nonce_b64="abcdefghijklmnop",
            ciphertext_b64="x",
            plaintext="should-never-be-here",
        )
    except Exception:
        return
    raise AssertionError("plaintext field must never be accepted by the envelope")
