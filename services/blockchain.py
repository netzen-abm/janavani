# Simple blockchain anchoring helper using web3.py
# This is intentionally lightweight: it sends transactions with the CID in the data field.
# For production, deploy a small contract with a storeHash(bytes32) method and call that instead.

import os
from web3 import Web3

WEB3_RPC = os.getenv("WEB3_RPC")
PRIVATE_KEY = os.getenv("CHAIN_PRIVATE_KEY")
ANCHOR_CONTRACT = os.getenv("ANCHOR_CONTRACT_ADDRESS")
GAS_PRICE_GWEI = os.getenv("GAS_PRICE_GWEI", "5")

w3 = Web3(Web3.HTTPProvider(WEB3_RPC)) if WEB3_RPC else None


def anchor_to_chain(content_hash: str) -> str:
    """Send a minimal tx with content_hash in the data field. Returns tx hash hex string."""
    if not w3 or not PRIVATE_KEY:
        raise RuntimeError("Web3 not configured (set WEB3_RPC and CHAIN_PRIVATE_KEY)")

    acct = w3.eth.account.from_key(PRIVATE_KEY)
    nonce = w3.eth.get_transaction_count(acct.address)
    data = content_hash.encode("utf-8").hex()
    tx = {
        "to": ANCHOR_CONTRACT or "0x0000000000000000000000000000000000000000",
        "value": 0,
        "gas": 200000,
        "gasPrice": w3.to_wei(GAS_PRICE_GWEI, "gwei"),
        "nonce": nonce,
        "data": "0x" + data,
    }
    signed = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
    return tx_hash.hex()
