"""BLE mesh helper (optional).

This is a lightweight, cross-platform skeleton for a BLE-based relay mesh. Full BLE mesh
on mobile requires platform-specific implementations (Android/iOS). This module provides a
simple relay abstraction you can use in Python environments that support BLE (Linux, macOS,
Windows with adapter) via bleak.

Design notes:
- Operates in two modes where possible:
  * scan_and_relay(): listens for advertisements/notifications and relays messages to peers.
  * send_packet(): sends a packet to discovered peers via GATT write/notify where possible.
- Real mobile mesh (multi-hop) needs persistent peer discovery and background services. Use this
  as a local prototype and reference implementation.

Environment:
- Install 'bleak' for BLE operations (pip install bleak).
- Many desktops cannot act as BLE peripheral; Linux with BlueZ + experimental support is best.
- On mobile, prefer native SDKs (this repo provides the network protocol and serialization used
  by mobile apps).
"""
from typing import Optional, Callable
import os
import asyncio

try:
    from bleak import BleakScanner, BleakClient, BleakGATTCharacteristic
except Exception:
    BleakScanner = None
    BleakClient = None

# UUIDs used for mesh service/characteristic (example; choose production-safe UUIDs)
MESH_SERVICE_UUID = os.getenv("MESH_SERVICE_UUID", "0000feed-0000-1000-8000-00805f9b34fb")
MESH_CHAR_UUID = os.getenv("MESH_CHAR_UUID", "0000beef-0000-1000-8000-00805f9b34fb")


async def scan_for_mesh_messages(timeout: int = 10, on_message: Optional[Callable] = None):
    """Scan for BLE devices and call on_message(payload_bytes) for any mesh-characteristic data.

    This function is a best-effort helper for prototyping; it won't create a full mesh on its own.
    """
    if not BleakScanner:
        raise RuntimeError("bleak not installed or platform doesn't support BLE scanning")

    devices = await BleakScanner.discover(timeout=timeout)
    for d in devices:
        # Attempt to connect and read characteristic if the device advertises the mesh service
        # Note: many devices won't allow this or may require pairing. Keep this simple for dev.
        try:
            client = BleakClient(d)
            await client.connect(timeout=5)
            try:
                if MESH_CHAR_UUID in await client.get_services().characteristics:
                    data = await client.read_gatt_char(MESH_CHAR_UUID)
                    if on_message:
                        on_message(bytes(data))
            finally:
                await client.disconnect()
        except Exception:
            continue


async def send_packet_to_peer(address: str, packet: bytes) -> bool:
    """Attempt to connect to a peer and write a mesh packet to the MESH_CHAR_UUID.

    Returns True on success, False on failure. Address is the BLE device address (platform-specific).
    """
    if not BleakClient:
        raise RuntimeError("bleak not installed or platform doesn't support BLE client")
    try:
        client = BleakClient(address)
        await client.connect(timeout=5)
        try:
            await client.write_gatt_char(MESH_CHAR_UUID, packet)
            return True
        finally:
            await client.disconnect()
    except Exception:
        return False


# High-level relay API

def publish_via_ble_mesh(packet: bytes, timeout: int = 5) -> dict:
    """Publish a packet to nearby peers via BLE. This is synchronous and uses asyncio internally.

    Returns a dict with seen_peers and successes. For production, run an asyncio service that
    continuously advertises and accepts writes.
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    results = {"attempted": 0, "succeeded": 0, "errors": []}

    async def _task():
        # Discover devices quickly and try to send packet to any connectable peers.
        devices = await BleakScanner.discover(timeout=timeout) if BleakScanner else []
        for d in devices:
            results["attempted"] += 1
            try:
                ok = await send_packet_to_peer(d.address, packet)
                if ok:
                    results["succeeded"] += 1
            except Exception as e:
                results["errors"].append(str(e))

    try:
        loop.run_until_complete(_task())
    finally:
        loop.close()
    return results
