"""Binary mesh packet format helper.

Packet layout (version 1):
- 1 byte: version
- 1 byte: msg_type (1=rating, 2=ack, 3=control)
- 2 bytes: payload length (big-endian)
- N bytes: payload (encrypted bytes)

This module provides pack/unpack helpers and is intentionally compact to fit BLE
MTU constraints. Use further compression if needed.
"""
import struct
from typing import Tuple

VERSION = 1

MSG_TYPE_RATING = 1
MSG_TYPE_ACK = 2
MSG_TYPE_CONTROL = 3


def pack_packet(msg_type: int, payload: bytes) -> bytes:
    if len(payload) > 0xFFFF:
        raise ValueError("Payload too large")
    header = struct.pack(
        ">BBH", VERSION, msg_type & 0xFF, len(payload) & 0xFFFF
    )
    return header + payload


def unpack_packet(packet: bytes) -> Tuple[int, bytes]:
    if len(packet) < 4:
        raise ValueError("Packet too short")
    version, msg_type, payload_len = struct.unpack(
        ">BBH", packet[:4]
    )
    if version != VERSION:
        raise ValueError(f"Unsupported version: {version}")
    if len(packet) != 4 + payload_len:
        raise ValueError("Invalid payload length")
    payload = packet[4:]
    return msg_type, payload
