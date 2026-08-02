# Janavani SLM + RAG POC

This branch (feat/slm-rag-poc) adds a minimal proof-of-concept for Retrieval-Augmented Generation using open-source components and small language models.

What this scaffold provides
- services/open_poc.py  -- quick local test for embeddings + FAISS retrieval (no server required)
- services/rag_agent.py -- build/load a FAISS index and run retrieval against it
- services/agent_tools.py -- local generator wrapper (uses HF transformers if configured), and helper tools
- services/agent_runner.py -- simple orchestration (retrieve -> generate)
- api/agent_api.py     -- FastAPI endpoints to ingest data, query retrieval, and generate complaint drafts
- requirements.txt     -- minimal Python dependencies

Step-by-step (one small step at a time)
1) Clone the repo and checkout the branch:
   git clone https://github.com/netzen-abm/janavani.git
   cd janavani
   git fetch origin
   git checkout feat/slm-rag-poc

2) Create & activate a venv (Linux / macOS):
   python3 -m venv .venv
   source .venv/bin/activate

3) Install dependencies (for the POC):
   pip install --upgrade pip
   pip install -r requirements.txt

4) Quick local retrieval test (no server):
   python services/open_poc.py

   You should see the index built and the top retrieved documents for the sample query.

5) Run the API server (optional):
   uvicorn api.agent_api:app --reload --port 8000

   Example curl flow:
   - Ingest some chunks:
     curl -X POST "http://127.0.0.1:8000/ingest" -H "Content-Type: application/json" -d '{"chunks": ["doc1 text...", "doc2 text..."]}'

   - Query retrieval:
     curl -X POST "http://127.0.0.1:8000/query" -H "Content-Type: application/json" -d '{"question":"How to file a municipal complaint?", "k":3}'

   - Generate a complaint (requires an index):
     curl -X POST "http://127.0.0.1:8000/generate_complaint" -H "Content-Type: application/json" -d '{"user_info": {"name":"A. Kumar"}, "facts":"Water supply cut for 3 months", "k":4}'

Notes on local SLMs and GPUs
- This scaffold defaults to a retrieval-first POC. Generation will use a local HF model if you set the environment variable LOCAL_LLM_MODEL to a model name or local path.
- Small models on CPU (e.g., GPT2) can run but quality is low. For useful drafts consider running a ggml/gguf model via llama.cpp or using a GPU-backed HF server (TGI / vLLM).

If you want, I can:
- Switch the generator to use llama.cpp / gpt4all and include scripts to run them locally (CPU-friendly).
- Add Docker + Docker Compose to run a local TGI server if you have a GPU.
- Open a PR now (I already pushed this branch). Tell me which next small step you want to take.
