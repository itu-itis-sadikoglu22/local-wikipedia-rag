import argparse

from app.vector_store import build_vector_store
from app.chat_cli import chat_loop


def main():
    parser = argparse.ArgumentParser(description="Local Wikipedia RAG")
    sub = parser.add_subparsers(dest="command", required=True)

    ingest_cmd = sub.add_parser("build-index", help="Build Chroma vector store")
    ingest_cmd.set_defaults(action="build-index")

    chat_cmd = sub.add_parser("chat", help="Start chat CLI")
    chat_cmd.add_argument("--context", action="store_true", help="Show retrieved context")
    chat_cmd.set_defaults(action="chat")

    args = parser.parse_args()

    if args.action == "build-index":
        build_vector_store()

    elif args.action == "chat":
        chat_loop(show_context=args.context)


if __name__ == "__main__":
    main()