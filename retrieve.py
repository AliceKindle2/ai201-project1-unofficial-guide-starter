"""
retrieve.py  —  Milestone 4 (Retrieval)
=======================================
Loads the ChromaDB collection built by embed_and_store.py and
exposes a retrieve() function that takes a plain-English query
and returns the top-k most similar chunks with full metadata.

Usage (interactive test):
    python retrieve.py

Or import in your generation script:
    from retrieve import retrieve
    results = retrieve("easy grader CS professor")

Dependencies (install once):
    pip install sentence-transformers chromadb
"""

from sentence_transformers import SentenceTransformer
import chromadb

# ── CONFIG ──────────────────────────────────────────────────────────────────
CHROMA_DIR  = "./chroma_db"
COLLECTION  = "utd_reviews"
MODEL_NAME  = "all-MiniLM-L6-v2"
TOP_K       = 5                  # spec §Retrieval Approach

# Load once at module level so repeated calls don't reload the model
_model      = None
_collection = None


def _load():
    global _model, _collection
    if _model is None:
        print(f"Loading model: {MODEL_NAME}")
        _model = SentenceTransformer(MODEL_NAME)
    if _collection is None:
        client      = chromadb.PersistentClient(path=CHROMA_DIR)
        _collection = client.get_collection(COLLECTION)
        print(f"Connected to collection '{COLLECTION}' "
              f"({_collection.count()} chunks)")


def retrieve(query: str, top_k: int = TOP_K) -> list[dict]:
    """
    Embed the query with all-MiniLM-L6-v2, query ChromaDB for
    the top_k most similar chunks, and return a list of dicts:

        {
            "rank":      int,          # 1 = most similar
            "score":     float,        # cosine similarity (0–1, higher = better)
            "text":      str,          # chunk text
            "source":    str,          # e.g. "Rate My Professor"
            "professor": str,          # populated when available
            "course":    str,          # populated when available
            "chunk_id":  str,
        }
    """
    _load()

    query_vec = _model.encode(query).tolist()

    results = _collection.query(
        query_embeddings=[query_vec],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )

    chunks = []
    docs       = results["documents"][0]
    metadatas  = results["metadatas"][0]
    distances  = results["distances"][0]
    ids        = results["ids"][0]

    for rank, (doc, meta, dist, cid) in enumerate(
            zip(docs, metadatas, distances, ids), start=1):
        # ChromaDB cosine distance = 1 - similarity; convert back
        score = round(1 - dist, 4)
        chunks.append({
            "rank":      rank,
            "score":     score,
            "text":      doc,
            "source":    meta.get("source",    ""),
            "professor": meta.get("professor", ""),
            "course":    meta.get("course",    ""),
            "chunk_id":  cid,
        })

    return chunks


def print_results(query: str, results: list[dict]) -> None:
    print(f"\nQuery: \"{query}\"")
    print("=" * 60)
    for r in results:
        print(f"\nRank {r['rank']}  |  score={r['score']}  |  {r['source']}", end="")
        if r["professor"]:
            print(f"  |  prof={r['professor']}", end="")
        if r["course"]:
            print(f"  |  course={r['course']}", end="")
        print()
        print(r["text"])
        print("-" * 60)


# ── INTERACTIVE TEST ────────────────────────────────────────────────────────
# These match the verification queries from your planning.md §Milestone 4

TEST_QUERIES = [
    "easy grader CS professor",
    "hardest courses at UTD",
    "professor who curved the exam",
]

if __name__ == "__main__":
    for q in TEST_QUERIES:
        results = retrieve(q)
        print_results(q, results)

    # Live prompt so you can type your own queries
    print("\n" + "=" * 60)
    print("Type a query to test (or 'quit' to exit):")
    while True:
        q = input("\n> ").strip()
        if q.lower() in ("quit", "exit", "q"):
            break
        if q:
            print_results(q, retrieve(q))