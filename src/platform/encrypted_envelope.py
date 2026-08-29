"""End-to-end encrypted envelope contract for data that must cross a boundary.

The server treats the payload as opaque ciphertext. Decryption keys remain on
user-controlled devices and are never accepted by this module.
"""
from __future__ import annotations

from pydantic import BaseModel, Field


class EncryptedEnvelope(BaseModel):
    version: str = Field(default="JNV-E2EE-1", min_length=1, max_length=32)
    algorithm: str = Field(default="AES-GCM-256", min_length=3, max_length=64)
    key_reference: str = Field(min_length=1, max_length=256)
    nonce_b64: str = Field(min_length=12, max_length=256)
    ciphertext_b64: str = Field(min_length=1, max_length=10_000_000)
    aad_b64: str | None = Field(default=None, max_length=4096)

    model_config = {"extra": "forbid"}


def assert_opaque(envelope: EncryptedEnvelope) -> EncryptedEnvelope:
    """Return an envelope without ever attempting to decrypt it."""
    return envelope
