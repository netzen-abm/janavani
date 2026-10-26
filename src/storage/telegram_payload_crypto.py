"""Cryptographic boundary for Telegram inbox payloads."""
from __future__ import annotations

import json
from typing import Any

from cryptography.fernet import Fernet, InvalidToken, MultiFernet


def build_fernet(keys: list[str]) -> MultiFernet | None:
    """Build an ordered decryption key ring; the first key is the active encryptor."""
    if not keys:
        return None
    try:
        return MultiFernet([Fernet(key.encode("ascii")) for key in keys])
    except (ValueError, UnicodeEncodeError) as exc:
        raise ValueError(
            "JANAVANI_TELEGRAM_INBOX_ENCRYPTION_KEYS must contain valid Fernet keys"
        ) from exc


def require_fernet(fernet: MultiFernet | None) -> MultiFernet:
    if fernet is None:
        raise RuntimeError(
            "JANAVANI_TELEGRAM_INBOX_ENCRYPTION_KEYS is required for durable Telegram payloads"
        )
    return fernet


def encode_payload(payload: dict[str, Any]) -> bytes:
    return json.dumps(payload, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def encrypt_payload(fernet: MultiFernet, payload: dict[str, Any]) -> bytes:
    return fernet.encrypt(encode_payload(payload))


def decrypt_payload(
    fernet: MultiFernet, update_id: int, encrypted_payload: bytes
) -> dict[str, Any]:
    """Decrypt in memory and verify the authenticated envelope matches its row key."""
    try:
        plaintext = fernet.decrypt(bytes(encrypted_payload))
    except InvalidToken as exc:
        raise ValueError("Telegram payload ciphertext cannot be decrypted") from exc
    payload = json.loads(plaintext.decode("utf-8"))
    if not isinstance(payload, dict) or payload.get("update_id") != update_id:
        raise ValueError("decrypted Telegram payload does not match its inbox key")
    return payload
