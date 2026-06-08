"""
retrieve.py — Hybrid Retrieval Pipeline
Combines ChromaDB cosine similarity (semantic) + BM25 keyword search.
Score merge: 0.6 * semantic + 0.4 * BM25. Returns top-k=5 results.
"""

from sentence_transformers import SentenceTransformer
import chromadb
from rank_bm25 import BM25Okapi

CHROMA_PATH = "chroma_db"
COLLECTION_NAME = "uci_professors"
MODEL_NAME = "all-MiniLM-L6-v2"

_model = None
_collection = None
_bm25 = None
_all_chunks = None  # [{id, text, source, professor}, ...]


def _load():
    """Lazy-load model, ChromaDB collection, and BM25 index (once per process)."""
    global _model, _collection, _bm25, _all_chunks
    if _model is not None:
        return

    _model = SentenceTransformer(MODEL_NAME)

    client = chromadb.PersistentClient(path=CHROMA_PATH)
    _collection = client.get_collection(COLLECTION_NAME)

    # Pull all stored chunks for BM25 (in-memory index)
    all_data = _collection.get(include=["documents", "metadatas"])
    _all_chunks = [
        {
            "id": chunk_id,
            "text": doc,
            "source": meta["source"],
            "professor": meta["professor"],
        }
        for chunk_id, doc, meta in zip(
            all_data["ids"], all_data["documents"], all_data["metadatas"]
        )
    ]

    tokenized = [chunk["text"].lower().split() for chunk in _all_chunks]
    _bm25 = BM25Okapi(tokenized)


def retrieve(query: str, top_k: int = 5) -> list[dict]:
    """
    Hybrid retrieval for a query string.
    Returns a list of up to top_k dicts:
      {text, source, professor, score, sem_score, bm25_score}
    """
    _load()

    query_embedding = _model.encode([query]).tolist()[0]

    # --- Semantic search: top-10 from ChromaDB ---
    sem_n = min(10, _collection.count())
    sem_results = _collection.query(
        query_embeddings=[query_embedding],
        n_results=sem_n,
        include=["documents", "metadatas", "distances"],
    )
    sem_ids = sem_results["ids"][0]
    sem_docs = sem_results["documents"][0]
    sem_metas = sem_results["metadatas"][0]
    # cosine distance in [0, 2]; convert to similarity [0, 1] then normalize
    sem_raw = [max(0.0, 1.0 - d) for d in sem_results["distances"][0]]
    max_sem = max(sem_raw) if sem_raw else 1.0
    sem_scores = [s / max_sem if max_sem > 0 else s for s in sem_raw]

    # --- BM25 search: top-10 across in-memory corpus ---
    bm25_raw = _bm25.get_scores(query.lower().split())
    top_bm25_idx = sorted(range(len(bm25_raw)), key=lambda i: bm25_raw[i], reverse=True)[:10]
    max_bm25 = bm25_raw[top_bm25_idx[0]] if top_bm25_idx else 1.0

    # --- Merge into candidate pool ---
    candidates = {}

    for chunk_id, doc, meta, sem_score in zip(sem_ids, sem_docs, sem_metas, sem_scores):
        candidates[chunk_id] = {
            "text": doc,
            "source": meta["source"],
            "professor": meta["professor"],
            "sem_score": sem_score,
            "bm25_score": 0.0,
        }

    for i in top_bm25_idx:
        chunk_id = _all_chunks[i]["id"]
        bm25_score = bm25_raw[i] / max_bm25 if max_bm25 > 0 else 0.0
        if chunk_id in candidates:
            candidates[chunk_id]["bm25_score"] = bm25_score
        else:
            chunk = _all_chunks[i]
            candidates[chunk_id] = {
                "text": chunk["text"],
                "source": chunk["source"],
                "professor": chunk["professor"],
                "sem_score": 0.0,
                "bm25_score": bm25_score,
            }

    for c in candidates.values():
        c["score"] = 0.6 * c["sem_score"] + 0.4 * c["bm25_score"]

    ranked = sorted(candidates.values(), key=lambda x: x["score"], reverse=True)
    return ranked[:top_k]


def print_results(query: str, results: list[dict]) -> None:
    """Pretty-print retrieval results for manual inspection."""
    print(f"\n{'='*65}")
    print(f"Query: {query}")
    print(f"{'='*65}")
    for rank, r in enumerate(results, 1):
        print(f"\n  [{rank}] score={r['score']:.3f}  "
              f"(sem={r['sem_score']:.3f}, bm25={r['bm25_score']:.3f})")
        print(f"  Source: {r['source']}  |  Professor: {r['professor']}")
        print(f"  {'-'*55}")
        print(f"  {r['text'][:400]}")
        if len(r["text"]) > 400:
            print("  ...")


if __name__ == "__main__":
    # Test with 3 evaluation plan queries
    TEST_QUERIES = [
        "Does Thornton curve ICS 33?",
        "Is Wong Ma worth taking even though he is hard?",
        "What is Shindler's grading structure like in ICS 46?",
    ]

    print("=== Retrieval Test — 3 Evaluation Queries ===")
    for query in TEST_QUERIES:
        results = retrieve(query)
        print_results(query, results)

    print("\n=== Done — inspect chunks above for relevance and score quality ===")
    print("Target: top result score > 0.5, chunks visibly on-topic.")
