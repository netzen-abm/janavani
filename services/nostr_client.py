# Nostr client helper (minimal, optional)
# Uses python-nostr: https://pypi.org/project/python-nostr/
# Add NOSTR_PRIVATE_KEY_HEX and NOSTR_RELAYS to .env

import os
import json
import time
from typing import List, Optional

try:
    from nostr.key import PrivateKey
    from nostr.event import Event
    from nostr.relay_manager import RelayManager
except Exception:
    # Library may be missing in dev; functions will raise if used without install.
    PrivateKey = None
    Event = None
    RelayManager = None

NOSTR_RELAYS = os.getenv("NOSTR_RELAYS", "wss://relay.damus.io").split(",")
NOSTR_PRIV_HEX = os.getenv("NOSTR_PRIVATE_KEY_HEX")

relay_manager = None
privkey = None

if RelayManager and PrivateKey and NOSTR_PRIV_HEX:
    try:
        privkey = PrivateKey.from_hex(NOSTR_PRIV_HEX)
        relay_manager = RelayManager()
        for r in NOSTR_RELAYS:
            relay_manager.add_relay(r.strip())
    except Exception:
        relay_manager = None


def publish_nostr_event(content: dict, kind: int = 1, tags: Optional[List[list]] = None) -> Optional[str]:
    """Publish a signed JSON payload to configured Nostr relays. Returns the event id or None on failure."""
    if not relay_manager or not privkey:
        raise RuntimeError("Nostr not configured (missing python-nostr or env vars)")

    relay_manager.open_connections()
    payload = json.dumps(content, separators=(",", ":"))
    ev = Event(public_key=privkey.public_key.hex(), content=payload, kind=kind, tags=tags or [])
    ev.sign(privkey.hex())
    relay_manager.publish_event(ev)
    relay_manager.close_connections()
    return getattr(ev, "id", None)
