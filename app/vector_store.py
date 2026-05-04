import json
from pathlib import Path

import chromadb

from app.chunker import build_chunks
from app.embedder import embed_text


RAW_DIR = Path("data/raw")
CHROMA_DIR = Path("data/chroma")
COLLECTION_NAME = "wiki_chunks"


def load_documents():
    documents = []

    for filename in ["person.json", "place.json"]:
        path = RAW_DIR / filename

        if not path.exists():
            raise FileNotFoundError(f"Missing raw data file: {path}")

        with open(path, "r", encoding="utf-8") as f:
            documents.extend(json.load(f))

    return documents


def get_collection():
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    collection = client.get_or_create_collection(name=COLLECTION_NAME)
    return collection


def build_vector_store():
    documents = load_documents()
    chunks = build_chunks(documents)

    collection = get_collection()

    print(f"Loaded {len(documents)} documents")
    print(f"Preparing to store {len(chunks)} chunks")

    for i, chunk in enumerate(chunks, start=1):
        existing = collection.get(ids=[chunk["id"]])
        if existing and existing.get("ids"):
            print(f"[{i}/{len(chunks)}] Skipping existing chunk: {chunk['id']}")
            continue

        print(f"[{i}/{len(chunks)}] Embedding {chunk['id']}")

        embedding = embed_text(chunk["text"])

        metadata = {
            "title": chunk["title"],
            "type": chunk["type"],
            "source": chunk["source"],
            "chunk_index": chunk["chunk_index"],
        }

        collection.add(
            ids=[chunk["id"]],
            documents=[chunk["text"]],
            embeddings=[embedding],
            metadatas=[metadata],
        )

    print("Vector store build complete.")


def query_vector_store(query, query_type=None, title=None, n_results=5):
    collection = get_collection()
    query_embedding = embed_text(query)

    where_clauses = []

    if query_type in ("person", "place"):
        where_clauses.append({"type": query_type})

    if title:
        where_clauses.append({"title": title})

    if len(where_clauses) == 0:
        where = None
    elif len(where_clauses) == 1:
        where = where_clauses[0]
    else:
        where = {"$and": where_clauses}

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
        where=where,
    )

    return results


def get_chunks_by_title(title, n_results=2):
    """
    Return the earliest chunks for a known entity.

    This is useful when the query explicitly names an entity.
    The first chunks usually contain the most general description,
    which is better for basic and comparison questions.
    """
    collection = get_collection()

    raw = collection.get(
        where={"title": title},
        include=["documents", "metadatas"],
    )

    ids = raw.get("ids", [])
    documents = raw.get("documents", [])
    metadatas = raw.get("metadatas", [])

    items = []

    for i in range(len(ids)):
        metadata = metadatas[i]
        text = documents[i]

        items.append(
            {
                "text": text,
                "metadata": metadata,
                "distance": None,
            }
        )

    items.sort(key=lambda x: x["metadata"].get("chunk_index", 999))

    return items[:n_results]