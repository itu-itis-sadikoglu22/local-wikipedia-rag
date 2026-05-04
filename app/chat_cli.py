from app.retriever import retrieve_context
from app.generator import generate_answer


def print_sources(results):
    print("\nRetrieved context:")
    print("-" * 60)

    for i, item in enumerate(results, start=1):
        meta = item["metadata"]
        title = meta.get("title", "Unknown")
        entity_type = meta.get("type", "unknown")
        source = meta.get("source", "")
        preview = item["text"][:300].replace("\n", " ")

        print(f"{i}. {title} ({entity_type})")
        print(f"   Source: {source}")
        print(f"   Preview: {preview}...")
        print()

    print("-" * 60)


def chat_loop(show_context=False):
    print("Local Wikipedia RAG Assistant")
    print("Type your question and press Enter.")
    print("Commands: /exit, /clear, /context on, /context off")
    print("-" * 60)

    while True:
        query = input("\nYou: ").strip()

        if not query:
            continue

        if query == "/exit":
            print("Goodbye.")
            break

        if query == "/clear":
            print("\n" * 5)
            continue

        if query == "/context on":
            show_context = True
            print("Context display enabled.")
            continue

        if query == "/context off":
            show_context = False
            print("Context display disabled.")
            continue

        if query.lower().startswith("compare"):
            retrieved = retrieve_context(query, n_results=2)
        else:
            retrieved = retrieve_context(query, n_results=3)
        results = retrieved["results"]

        if show_context:
            print_sources(results)

        answer = generate_answer(query, results)

        print("\nAssistant:")
        print(answer)