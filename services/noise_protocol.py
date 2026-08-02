"""Noise protocol session helper.

This module provides a small abstraction over the Noise protocol for establishing encrypted
sessions between peers. It is intentionally minimal: for production use, pick a battle-tested
library and thoroughly review handshake patterns.

Dependencies: the 'noiseprotocol' PyPI package (pip install noiseprotocol) or an alternative.
"""
import os

try:
    from noise.connection import NoiseConnection
except Exception:
    NoiseConnection = None


def create_initiator(local_private_key: bytes = None):
    if not NoiseConnection:
        raise RuntimeError("noiseprotocol not installed")
    n = NoiseConnection.from_name("Noise_NN_25519_ChaChaPoly_BLAKE2s")
    n.set_as_initiator()
    n.set_key_pair_from_private_bytes("s", local_private_key) if local_private_key else None
    n.start_handshake()
    return n


def create_responder(local_private_key: bytes = None):
    if not NoiseConnection:
        raise RuntimeError("noiseprotocol not installed")
    n = NoiseConnection.from_name("Noise_NN_25519_ChaChaPoly_BLAKE2s")
    n.set_as_responder()
    n.set_key_pair_from_private_bytes("s", local_private_key) if local_private_key else None
    n.start_handshake()
    return n


def handshake_step(noise_conn: "NoiseConnection", incoming: bytes) -> bytes:
    """Feed incoming handshake bytes and return bytes to send (or b'' if none)."""
    if not NoiseConnection:
        raise RuntimeError("noiseprotocol not installed")
    return noise_conn.read_message(incoming)


def encrypt_message(noise_conn: "NoiseConnection", plaintext: bytes) -> bytes:
    if not NoiseConnection:
        raise RuntimeError("noiseprotocol not installed")
    return noise_conn.encrypt(plaintext)


def decrypt_message(noise_conn: "NoiseConnection", ciphertext: bytes) -> bytes:
    if not NoiseConnection:
        raise RuntimeError("noiseprotocol not installed")
    return noise_conn.decrypt(ciphertext)
