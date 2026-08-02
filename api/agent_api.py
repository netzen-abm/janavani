"""FastAPI endpoints for the SLM + RAG POC and decentralized publish flow.

Run: uvicorn api.agent_api:app --reload --port 8000
"""
import os
import json
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from services import rag_agent, agent_runner

# Optional decentralized helpers (import at runtime to keep optional)
try:
    from services.storage_ipfs import add_bytes_to_ipfs
except Exception:
    add_bytes_to_ipfs = None

try:
    from services.nostr_client import publish_nostr_event
except Exception:
    publish_nostr_event = None

try:
    from services.blockchain import anchor_to_chain
except Exception:
    anchor_to_chain = None

app = FastAPI(title="Janavani SLM+RAG POC + Decentralized Publish")


class IngestRequest(BaseModel):
    chunks: List[str]


class QueryRequest(BaseModel):
    question: str
    k: int = 4


class ComplaintRequest(BaseModel):
    user_info: dict
    facts: str
    k: int = 6


class RatingPayload(BaseModel):
    user: Optional[str]
    rating: int
    text: Optional[str]
    metadata: Optional[dict] = None


@app.post("/ingest")
async def ingest(req: IngestRequest):
    if not req.chunks:
        raise HTTPException(status_code=400, detail="No chunks provided")
    rag_agent.build_faiss_index(req.chunks)
    return {"status": "ok", "indexed_chunks": len(req.chunks)}


@app.post("/query")
async def query(req: QueryRequest):
    try:
        hits = rag_agent.retrieve(req.question, k=req.k)
        return {"results": hits}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Index not found. Run /ingest first.")


@app.post("/generate_complaint")
async def generate_complaint(req: ComplaintRequest):
    try:
        letter = agent_runner.generate_complaint(req.user_info, req.facts, k=req.k)
        return {"complaint": letter}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Index not found. Run /ingest first.")


@app.post("/rating/publish")
async def publish_rating(payload: RatingPayload):
    """End-to-end example: serialize rating -> IPFS -> Nostr -> optional blockchain anchor.

    This endpoint is optional and will continue working even if decentralized services are
    not configured. The helpers live under services/ and are imported only if available.
    """
    # 1) Serialize rating
    data_bytes = json.dumps(payload.dict(), separators=(",", ":")).encode("utf-8")

    # 2) Add to IPFS (returns CID)
    cid = None
    if add_bytes_to_ipfs:
        try:
            cid = add_bytes_to_ipfs(data_bytes)
        except Exception as e:
            # IPFS failed — surface a 500 since storage is a core step for this flow
            raise HTTPException(status_code=500, detail=f"IPFS add failed: {e}")
    else:
        # IPFS not configured; respond with a helpful error
        raise HTTPException(status_code=500, detail="IPFS helper not available. See .env.example and docs/decentralized.md")

    # 3) Publish Nostr event (optional)
    nostr_event_id = None
    if publish_nostr_event:
        try:
            nostr_event_id = publish_nostr_event({"type": "rating", "cid": cid})
        except Exception:
            # Don't fail the whole request if Nostr isn't available — just continue
            nostr_event_id = None

    # 4) Optionally anchor the CID on-chain (if configured)
    tx_hash = None
    if anchor_to_chain and os.getenv("WEB3_RPC") and os.getenv("CHAIN_PRIVATE_KEY"):
        try:
            tx_hash = anchor_to_chain(cid)
        except Exception:
            tx_hash = None

    return {"cid": cid, "nostr_event_id": nostr_event_id, "tx_hash": tx_hash}
