"""
embed_and_store.py  —  Milestone 4 (Embedding + Vector Store)
=============================================================
Reads chunks.json produced by chunk_text.py, embeds every chunk
with all-MiniLM-L6-v2, and stores the vectors + metadata in a
persistent ChromaDB collection saved to ./chroma_db/.

Run once before retrieval:
    python embed_and_store.py

Dependencies (install once):
    pip install sentence-transformers chromadb
"""

import json
import os
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings

# ── CONFIG ──────────────────────────────────────────────────────────────────
CHUNKS_FILE   = "chunks.json"          # output of chunk_text.py
CHROMA_DIR    = "./chroma_db"          # persistent storage folder
COLLECTION    = "utd_reviews"          # name inside ChromaDB
MODEL_NAME    = "all-MiniLM-L6-v2"    # embedding model (spec §Retrieval Approach)
BATCH_SIZE    = 64                     # embed this many chunks at a time


def load_chunks(path: str) -> list[dict]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def build_metadata(chunk: dict) -> dict:
    """
    ChromaDB metadata values must be str | int | float | bool.
    Pull every useful field; fall back to empty string if absent.
    """
    return {
        "source":    chunk.get("source",    ""),
        "professor": chunk.get("professor", ""),
        "course":    chunk.get("course",    ""),
        "chars":     chunk.get("chars",     0),
    }


def embed_and_store(chunks: list[dict]) -> chromadb.Collection:
    print(f"Loading model: {MODEL_NAME}")
    model = SentenceTransformer(MODEL_NAME)

    print(f"Connecting to ChromaDB at {CHROMA_DIR}")
    client = chromadb.PersistentClient(path=CHROMA_DIR)

    # Delete existing collection so re-runs start fresh
    try:
        client.delete_collection(COLLECTION)
        print(f"Deleted existing collection '{COLLECTION}'")
    except Exception:
        pass

    collection = client.create_collection(
        name=COLLECTION,
        metadata={"hnsw:space": "cosine"},   # cosine similarity (spec §Retrieval)
    )

    texts     = [c["text"]       for c in chunks]
    ids       = [c["chunk_id"]   for c in chunks]
    metadatas = [build_metadata(c) for c in chunks]

    # Embed in batches so progress is visible
    total = len(texts)
    print(f"Embedding {total} chunks in batches of {BATCH_SIZE}...")
    all_embeddings = []
    for start in range(0, total, BATCH_SIZE):
        batch = texts[start : start + BATCH_SIZE]
        vecs  = model.encode(batch, show_progress_bar=False).tolist()
        all_embeddings.extend(vecs)
        done = min(start + BATCH_SIZE, total)
        print(f"  {done}/{total} embedded")

    print("Storing in ChromaDB...")
    collection.add(
        ids        = ids,
        embeddings = all_embeddings,
        documents  = texts,
        metadatas  = metadatas,
    )

    print(f"\nDone. {collection.count()} chunks stored in '{COLLECTION}'.")
    return collection


if __name__ == "__main__":
    chunks = load_chunks(CHUNKS_FILE)
    print(f"Loaded {len(chunks)} chunks from {CHUNKS_FILE}")
    embed_and_store(chunks)
    print(f"\nVector store saved to {CHROMA_DIR}/")
    print("Next step: run retrieve.py to test queries.")