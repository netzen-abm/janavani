"""FastAPI endpoints for the SLM + RAG POC.

Endpoints:
- POST /ingest  -> store provided chunks into FAISS index
- POST /query   -> simple retrieval (returns top-k docs)
- POST /generate_complaint -> orchestration: retrieve + generate draft

Run: uvicorn api.agent_api:app --reload --port 8000
"""
import os
from typing import List
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from services import rag_agent, agent_runner

app = FastAPI(title="Janavani SLM+RAG POC")


class IngestRequest(BaseModel):
    chunks: List[str]


class QueryRequest(BaseModel):
    question: str
    k: int = 4


class ComplaintRequest(BaseModel):
    user_info: dict
    facts: str
    k: int = 6


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
