"""
RAG retrieval using ChromaDB (exercise implementation scaffold).
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import List

sys.path.insert(0, str(Path(__file__).parent))
from documents import Document, load_documents  # noqa: E402


def _require_chroma():
    try:
        import chromadb  # noqa: F401
        return chromadb
    except ImportError as exc:
        raise RuntimeError("chromadb is required for this exercise") from exc


def build_collection(name: str = "rag_docs", path: str = "labs/01/data/chroma"):
    chromadb = _require_chroma()
    client = chromadb.PersistentClient(path=path)
    return client.get_or_create_collection(name=name)


def index_documents(collection, docs: List[Document]) -> None:
    ids = [doc.doc_id for doc in docs]
    texts = [doc.content for doc in docs]
    metadatas = [{"title": doc.title, "tags": doc.tags} for doc in docs]
    collection.upsert(ids=ids, documents=texts, metadatas=metadatas)


def retrieve(query: str, top_k: int = 2) -> List[Document]:
    docs = load_documents("labs/01/data/documents.json")
    collection = build_collection()
    index_documents(collection, docs)
    results = collection.query(query_texts=[query], n_results=top_k)
    retrieved = []
    for idx, doc_id in enumerate(results["ids"][0]):
        match = next(doc for doc in docs if doc.doc_id == doc_id)
        retrieved.append(match)
    return retrieved


if __name__ == "__main__":
    results = retrieve("What is RAG?", top_k=2)
    print("Retrieved Documents:")
    for doc in results:
        print(f"- {doc.title}")
