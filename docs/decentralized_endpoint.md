# docs: note about the new example endpoint

The branch provides an example endpoint `/rating/publish` in `api/agent_api.py`.
This demonstrates a minimal end-to-end flow:
- Serialize the rating payload
- Add the payload bytes to IPFS (returns CID)
- Publish a signed Nostr event containing the CID (optional)
- Optionally anchor the CID on-chain if WEB3_RPC and CHAIN_PRIVATE_KEY are set

See `api/agent_api.py` for implementation details and `docs/decentralized.md` for setup.
