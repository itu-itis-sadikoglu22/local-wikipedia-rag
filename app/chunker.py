MAX_DOC_CHARS = 12000


def chunk_text(text, chunk_size=1200, overlap=150):
    """
    Split text into overlapping chunks.

    For this local demo, very long Wikipedia pages are capped to keep
    ingestion and embedding practical on a laptop.
    """
    if not text:
        return []

    text = text[:MAX_DOC_CHARS]

    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        start += chunk_size - overlap

    return chunks


def build_chunks(documents):
    """
    Convert raw documents into chunk records with metadata.
    """
    all_chunks = []

    for doc in documents:
        title = doc["title"]
        entity_type = doc["type"]
        source = doc.get("source", "")
        text = doc["text"]

        chunks = chunk_text(text)

        for i, chunk in enumerate(chunks):
            safe_title = title.replace(" ", "_").replace("/", "_")

            all_chunks.append(
                {
                    "id": f"{entity_type}_{safe_title}_{i}",
                    "title": title,
                    "type": entity_type,
                    "source": source,
                    "chunk_index": i,
                    "text": chunk,
                }
            )

    return all_chunks