import json
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError


OLLAMA_EMBED_URL = "http://localhost:11434/api/embeddings"
EMBED_MODEL = "nomic-embed-text"


def embed_text(text):
    payload = {
        "model": EMBED_MODEL,
        "prompt": text,
    }

    data = json.dumps(payload).encode("utf-8")

    request = Request(
        OLLAMA_EMBED_URL,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urlopen(request, timeout=60) as response:
            raw = response.read().decode("utf-8")
            result = json.loads(raw)
            return result["embedding"]

    except HTTPError as e:
        raise RuntimeError(f"Ollama embedding HTTP error: {e.code}")

    except URLError as e:
        raise RuntimeError(
            f"Could not connect to Ollama. Make sure Ollama is running. Details: {e.reason}"
        )

    except Exception as e:
        raise RuntimeError(f"Embedding failed: {e}")