import chromadb
from chromadb.config import Settings
from pathlib import Path
from rag.embeddings import embed_texts, embed_query
import json, uuid

# Persist ChromaDB on disk
DB_PATH = Path(__file__).parent / "chroma_db"
DB_PATH.mkdir(exist_ok=True)

_client     = None
_collection = None

COLLECTION_NAME = "rbi_guidelines"


def get_collection():
    global _client, _collection
    if _collection is None:
        _client = chromadb.PersistentClient(
            path=str(DB_PATH),
            settings=Settings(anonymized_telemetry=False)
        )
        _collection = _client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"}
        )
    return _collection


def ingest_documents(documents: list[dict]):
    """
    Ingest RBI circulars into ChromaDB.
    Each doc: { "id": str, "text": str, "source": str, "category": str }
    """
    collection = get_collection()

    texts      = [d["text"]   for d in documents]
    ids        = [d.get("id", str(uuid.uuid4())) for d in documents]
    metadatas  = [{"source": d.get("source", ""), "category": d.get("category", "")} for d in documents]
    embeddings = embed_texts(texts)

    collection.upsert(
        ids        = ids,
        documents  = texts,
        metadatas  = metadatas,
        embeddings = embeddings,
    )
    print(f"✅ Ingested {len(documents)} documents into ChromaDB")


def search_guidelines(query: str, top_k: int = 3, category: str = None) -> list[dict]:
    """
    Search RBI guidelines relevant to a query.
    Used to ground GPT-4o responses in real RBI rules.
    """
    collection = get_collection()

    where_filter = {"category": category} if category else None

    results = collection.query(
        query_embeddings = [embed_query(query)],
        n_results        = top_k,
        where            = where_filter,
        include          = ["documents", "metadatas", "distances"],
    )

    output = []
    for i, doc in enumerate(results["documents"][0]):
        output.append({
            "text":     doc,
            "source":   results["metadatas"][0][i].get("source", ""),
            "category": results["metadatas"][0][i].get("category", ""),
            "score":    round(1 - results["distances"][0][i], 3),
        })

    return output


def get_stats() -> dict:
    """Return collection stats."""
    collection = get_collection()
    return {"total_documents": collection.count(), "collection": COLLECTION_NAME}