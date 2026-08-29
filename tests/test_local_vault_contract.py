from src.platform.encrypted_envelope import EncryptedEnvelope
from src.platform.local_vault import LocalVault


class MemoryVault:
    def __init__(self) -> None:
        self.data: dict[str, EncryptedEnvelope] = {}

    def put(self, key: str, envelope: EncryptedEnvelope) -> None:
        self.data[key] = envelope

    def get(self, key: str) -> EncryptedEnvelope | None:
        return self.data.get(key)

    def delete(self, key: str) -> None:
        self.data.pop(key, None)

    def keys(self) -> list[str]:
        return list(self.data)


def test_local_vault_stores_only_opaque_envelopes() -> None:
    vault: LocalVault = MemoryVault()
    envelope = EncryptedEnvelope(
        key_reference="device-key-1",
        nonce_b64="abcdefghijklmnop",
        ciphertext_b64="opaque-ciphertext",
    )
    vault.put("case/JNV-TEST", envelope)
    assert vault.get("case/JNV-TEST") == envelope
    assert vault.keys() == ["case/JNV-TEST"]
    vault.delete("case/JNV-TEST")
    assert vault.get("case/JNV-TEST") is None
