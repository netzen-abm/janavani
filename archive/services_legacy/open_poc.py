# services/open_poc.py
"""
Minimal FAISS + sentence-transformers retrieval POC.
Run: python services/open_poc.py

This is a simple script to verify embeddings + FAISS retrieval work on your machine.
"""
from sentence_transformers import SentenceTransformer
import faiss

EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


def build_faiss_index(texts, embed_model_name=EMBED_MODEL):
    embedder = SentenceTransformer(embed_model_name)
    vectors = embedder.encode(texts, show_progress_bar=False, convert_to_numpy=True)
    dim = vectors.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(vectors)
    return index, vectors, embedder


def retrieve(index, embedder, texts, query, k=3):
    qv = embedder.encode([query], convert_to_numpy=True)
    D, I = index.search(qv, k)
    results = []
    for dist, idx in zip(D[0], I[0]):
        results.append({"score": float(dist), "text": texts[int(idx)]})
    return results


if __name__ == "__main__":
    # SAMPLE docs: replace with your real small corpus later
    docs = [
        "Consumer Protection Act: How to file a complaint against a public official for unfair practices.",
        "Municipal complaints: steps to report poor municipal services and timeline for response.",
        "Template: Formal complaint letter to the local municipal commissioner about water supply issues.",
        "Constitutional provisions for public services and citizens' remedies under the law.",
        "Past case: court ruled in favor of citizens when officers failed to provide service after repeated requests."
    ]

    print("Building index (this may take a few seconds)...")
    index, vectors, embedder = build_faiss_index(docs)
    print("Index built. Number of docs:", len(docs))

    query = "How to write a complaint about water supply not being fixed?"
    print("\nQuery:", query)
    hits = retrieve(index, embedder, docs, query, k=3)

    print("\nTop results:")
    for i, h in enumerate(hits, start=1):
        print(f"{i}. score={h['score']:.4f} text={h['text'][:200]}")
