# IPFS storage helper using ipfshttpclient
# Programmatic and easy to run with a local go-ipfs daemon (daemon exposes API at /ip4/127.0.0.1/tcp/5001)

import os
from typing import Tuple

try:
    import ipfshttpclient
except Exception:
    ipfshttpclient = None

IPFS_ADDR = os.getenv("IPFS_API_ADDR", "/ip4/127.0.0.1/tcp/5001")


def add_bytes_to_ipfs(data: bytes) -> str:
    """Adds bytes to IPFS and returns the CID string."""
    if not ipfshttpclient:
        raise RuntimeError("ipfshttpclient not installed")
    with ipfshttpclient.connect(IPFS_ADDR) as client:
        res = client.add_bytes(data)
    return res


def get_from_ipfs(cid: str) -> bytes:
    if not ipfshttpclient:
        raise RuntimeError("ipfshttpclient not installed")
    with ipfshttpclient.connect(IPFS_ADDR) as client:
        return client.cat(cid)
