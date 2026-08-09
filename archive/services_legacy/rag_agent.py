import os
import faiss
import pickle
from typing import List, Tuple
from sentence_transformers import SentenceTransformer

# File paths (configurable via env)
INDEX_DIR = os.getenv("RAG_INDEX_DIR", "data")
INDEX_PATH = os.path.join(INDEX_DIR, "faiss.index")
TEXTS_PATH = os.path.join(INDEX_DIR, "texts.pkl")
EMBED_MODEL = os.getenv("EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2")


def _ensure_index_dir():
    os.makedirs(INDEX_DIR, exist_ok=True)


def build_faiss_index(texts: List[str], embed_model_name: str = EMBED_MODEL) -> None:
    """Build and persist a FAISS index from `texts`.

    This writes faiss index to INDEX_PATH and texts to TEXTS_PATH.
    """
    _ensure_index_dir()
    embedder = SentenceTransformer(embed_model_name)
    vectors = embedder.encode(texts, show_progress_bar=True, convert_to_numpy=True)
    dim = vectors.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(vectors)
    faiss.write_index(index, INDEX_PATH)
    with open(TEXTS_PATH, "wb") as f:
        pickle.dump(texts, f)


def load_faiss_index(embed_model_name: str = EMBED_MODEL) -> Tuple[SentenceTransformer, faiss.Index, List[str]]:
    """Load persisted FAISS index and return (embedder, index, texts).

    Raises FileNotFoundError if index or texts are missing.
    """
    if not os.path.exists(INDEX_PATH) or not os.path.exists(TEXTS_PATH):
        raise FileNotFoundError("FAISS index or texts not found. Run build_faiss_index first.")
    embedder = SentenceTransformer(embed_model_name)
    index = faiss.read_index(INDEX_PATH)
    with open(TEXTS_PATH, "rb") as f:
        texts = pickle.load(f)
    return embedder, index, texts


def retrieve(query: str, k: int = 4, embed_model_name: str = EMBED_MODEL):
    """Retrieve top-k documents for `query` from the persisted index."""
    embedder, index, texts = load_faiss_index(embed_model_name=embed_model_name)
    qv = embedder.encode([query], convert_to_numpy=True)
    D, I = index.search(qv, k)
    results = []
    for dist, idx in zip(D[0], I[0]):
        results.append({"score": float(dist), "text": texts[int(idx)]})
    return results
