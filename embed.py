"""
embed.py — Embedding and Storage Pipeline
Loads chunks from chunk.py, embeds with all-MiniLM-L6-v2, and upserts into
a ChromaDB collection called 'uci_professors' persisted to /chroma_db.
Metadata stored per chunk: source filename and professor name.
"""

from sentence_transformers import SentenceTransformer
import chromadb
from chunk import chunk_documents
from ingest import load_documents

CHROMA_PATH = "chroma_db"
COLLECTION_NAME = "uci_professors"
MODEL_NAME = "all-MiniLM-L6-v2"
BATCH_SIZE = 100


def embed_and_store() -> int:
    """
    Full pipeline: load -> chunk -> embed -> store in ChromaDB.
    Returns the number of chunks stored.
    """
    print("=== Step 1: Loading and chunking documents ===\n")
    documents = load_documents()
    chunks = chunk_documents(documents)
    print(f"\nTotal chunks to embed: {len(chunks)}")

    print("\n=== Step 2: Loading embedding model ===")
    model = SentenceTransformer(MODEL_NAME)
    print(f"Model loaded: {MODEL_NAME}")

    print("\n=== Step 3: Embedding all chunks ===")
    texts = [c["text"] for c in chunks]
    embeddings = model.encode(texts, show_progress_bar=True, batch_size=32)
    print(f"Embeddings shape: {embeddings.shape}")

    print("\n=== Step 4: Storing in ChromaDB ===")
    client = chromadb.PersistentClient(path=CHROMA_PATH)

    # Drop and recreate collection so re-runs are idempotent
    try:
        client.delete_collection(COLLECTION_NAME)
        print(f"Deleted existing collection '{COLLECTION_NAME}'")
    except Exception:
        pass

    collection = client.create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )

    ids = [f"chunk_{i}" for i in range(len(chunks))]
    metadatas = [{"source": c["source"], "professor": c["professor"]} for c in chunks]

    for batch_start in range(0, len(chunks), BATCH_SIZE):
        batch_end = min(batch_start + BATCH_SIZE, len(chunks))
        try:
            collection.add(
                ids=ids[batch_start:batch_end],
                embeddings=embeddings[batch_start:batch_end].tolist(),
                documents=texts[batch_start:batch_end],
                metadatas=metadatas[batch_start:batch_end],
            )
        except Exception as e:
            print(f"  WARNING: batch {batch_start}-{batch_end} failed: {e}")

    stored = collection.count()
    print(f"\nStored {stored} chunks in collection '{COLLECTION_NAME}' at '{CHROMA_PATH}'")
    return stored


if __name__ == "__main__":
    count = embed_and_store()
    print(f"\n=== Checkpoint: {count} chunks in ChromaDB ===")
    if count < 50:
        print("  WARNING: fewer than 50 chunks — check ingest/chunk pipeline.")
    else:
        print("  OK: ready for retrieval.")
