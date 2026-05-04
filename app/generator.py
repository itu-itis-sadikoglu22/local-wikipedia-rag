import json
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError


OLLAMA_GENERATE_URL = "http://localhost:11434/api/generate"
LLM_MODEL = "llama3.2:1b"


def build_prompt(query, context_items):
    context_text = ""

    for i, item in enumerate(context_items, start=1):
        meta = item["metadata"]
        title = meta.get("title", "Unknown")
        source = meta.get("source", "")
        text = item["text"]

        context_text += f"\n[Source {i}] Title: {title}\nURL: {source}\n{text}\n"

        prompt = f"""
You are a local Wikipedia RAG assistant.

Answer the question using only the retrieved context below.

Strict rules:
- Do not use outside knowledge.
- Do not guess or fill missing facts from memory.
- If the answer is not clearly supported by the context, say exactly: I don't know.
- For comparison questions, compare only facts that are explicitly present in the context.
- Do not mention height, dates, locations, uses, achievements, or measurements unless they appear in the context.
- If a detail appears for one item but not the other, say that the context only provides that detail for one item.
- Keep the answer short and factual.

Context:
{context_text}

Question:
{query}

Answer:
""".strip()

    return prompt


def generate_answer(query, context_items):
    prompt = build_prompt(query, context_items)

    payload = {
        "model": LLM_MODEL,
        "prompt": prompt,
        "stream": False,
    }

    data = json.dumps(payload).encode("utf-8")

    request = Request(
        OLLAMA_GENERATE_URL,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urlopen(request, timeout=180) as response:
            raw = response.read().decode("utf-8")
            result = json.loads(raw)
            return result.get("response", "").strip()

    except HTTPError as e:
        return f"Generation failed. Ollama HTTP error: {e.code}"

    except URLError as e:
        return f"Generation failed. Could not connect to Ollama: {e.reason}"

    except Exception as e:
        return f"Generation failed: {e}"