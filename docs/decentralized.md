# Decentralized integrations: design notes and how-to

This document explains the optional decentralized/hybrid integrations added on the feature branch `feat/decentralized-integrations`.

Overview
- We provide optional helpers for: Nostr (pub/sub), IPFS (storage), blockchain anchoring (web3), and Nym proxying (network anonymity).
- These are intentionally optional: the core app does not require them. They live under `services/` and an example dev docker-compose is provided in `docker-compose.decentralized.yml`.

Quick start (local)
1. Start IPFS and Ganache for local testing:
   docker-compose -f docker-compose.decentralized.yml up -d
2. Install new Python deps:
   pip install -r requirements.txt
3. Configure `.env` from `.env.example` and set values for the services you want to test (e.g. IPFS_API_ADDR, NOSTR_PRIVATE_KEY_HEX).
4. Use the helpers in `services/` from your FastAPI endpoints. Example flow:
   - Save rating locally
   - Serialize rating -> bytes
   - add_bytes_to_ipfs() -> returns CID
   - publish_nostr_event({"type":"rating","cid":cid})
   - optionally anchor_to_chain(cid)

Notes & next steps
- Freenet integration was intentionally omitted from the first pass because IPFS is easier to automate and test. If you require Freenet specifically, I can add an optional `services/storage_freenet.py` and docs for running a local Freenet node.
- For on-chain anchoring in production, deploy a small contract that stores hashes (cheaper than embedding long data in tx payloads).
- Nym requires running a nym-client locally and configuring the SOCKS5 endpoint. This is left as an ops step; the helper will use NYM_SOCKS env var.

What I committed
- services/nostr_client.py
- services/storage_ipfs.py
- services/blockchain.py
- services/nym_proxy.py
- docker-compose.decentralized.yml
- .env.example (appended variables)
- updated requirements.txt (added optional libs)
- docs/decentralized.md

Next I can:
- Open a PR from this branch to main with these changes (I can create the PR description and title for you).
- Implement an example FastAPI endpoint that demonstrates the full flow (rating -> IPFS -> Nostr -> optional blockchain anchor).

Tell me which of those you'd like next, or if you want me to also add Freenet support in the same branch.
