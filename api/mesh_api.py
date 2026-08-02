"""Extend API with a mesh publish endpoint that attempts BLE mesh delivery and falls back to Nostr.

The endpoint will:
 - serialize and optionally store the payload in IPFS (if configured)
 - prepare a binary packet, encrypt it via Noise (if available), and broadcast via BLE mesh
 - publish to Nostr as a fallback/fanout if network is available
"""
from fastapi import APIRouter, HTTPException
import json
import os
from services.binary_protocol import pack_packet, MSG_TYPE_RATING

# Optional imports
try:
    from services.noise_protocol import create_initiator, encrypt_message
except Exception:
    create_initiator = None
    encrypt_message = None

try:
    from services.ble_mesh import publish_via_ble_mesh
except Exception:
    publish_via_ble_mesh = None

try:
    from services.storage_ipfs import add_bytes_to_ipfs
except Exception:
    add_bytes_to_ipfs = None

try:
    from services.nostr_client import publish_nostr_event
except Exception:
    publish_nostr_event = None

router = APIRouter()


@router.post("/rating/mesh_publish")
async def mesh_publish(payload: dict):
    # 1) serialize
    data_bytes = json.dumps(payload, separators=(",", ":")).encode("utf-8")

    # 2) optional IPFS store (get CID)
    cid = None
    if add_bytes_to_ipfs:
        try:
            cid = add_bytes_to_ipfs(data_bytes)
        except Exception:
            cid = None

    # 3) prepare packet
    pkt_payload = data_bytes
    # 3a) encrypt if noise available
    if create_initiator and encrypt_message:
        try:
            # For demo we create a local initiator without keys; real flow requires peer keys
            nc = create_initiator()
            # In practice, handshake must be performed over BLE; here we assume session established
            pkt_payload = encrypt_message(nc, data_bytes)
        except Exception:
            pkt_payload = data_bytes

    packet = pack_packet(MSG_TYPE_RATING, pkt_payload)

    # 4) attempt BLE mesh publish (best-effort)
    mesh_result = None
    if publish_via_ble_mesh:
        try:
            mesh_result = publish_via_ble_mesh(packet)
        except Exception as e:
            mesh_result = {"error": str(e)}
    else:
        mesh_result = {"info": "BLE mesh helper not available"}

    # 5) fallback / fanout to Nostr if available (do not fail on nostr errors)
    nostr_id = None
    try:
        if publish_nostr_event:
            nostr_id = publish_nostr_event({"type": "rating", "cid": cid})
    except Exception:
        nostr_id = None

    return {"cid": cid, "mesh": mesh_result, "nostr_event_id": nostr_id}
