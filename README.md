pip install -r requirements.txt
ollama pull llama3.2:1b
ollama pull nomic-embed-text
python app/wiki_ingest.py
python -m app.main build-index
python -m app.main chat --context


# Local Wikipedia RAG Assistant

This project is a local Retrieval Augmented Generation system that answers questions about famous people and famous places using Wikipedia data. The system runs on localhost and uses local resources for ingestion, retrieval, embeddings, vector storage, and answer generation.

The goal is to build a simplified ChatGPT-style assistant that does not rely on an external LLM API.

## What the system does

The system can:

- ingest Wikipedia data for famous people and places
- split long documents into overlapping chunks
- generate local embeddings using Ollama
- store embeddings in a local Chroma vector store
- retrieve relevant chunks for a user question
- generate answers using a local language model
- return "I don't know" when the answer is not available in the local data
- optionally show retrieved context in the CLI

## Data ingested

The project ingests at least:

- 20 famous people
- 20 famous places

The required minimum entities are included, such as Albert Einstein, Marie Curie, Nikola Tesla, Eiffel Tower, Great Wall of China, Hagia Sophia, Statue of Liberty, and Mount Everest.

Wikipedia data is stored locally under:

```text
data/raw/
Design choice: one vector store with metadata

This project uses one Chroma vector store with metadata instead of two separate vector stores.

Each chunk has metadata such as:

title
type: person or place
source
chunk index

This makes the system easier to manage while still allowing filtering by person/place when needed. It also supports mixed questions, such as comparing a person and a place or comparing two entities.

Chunking strategy

Documents are split into fixed-size overlapping chunks.

The current strategy:

caps very long Wikipedia pages to keep local processing practical
uses overlapping chunks to preserve context between adjacent parts
stores metadata with every chunk

This is a practical tradeoff for running the project on a laptop.

Local models

This project uses Ollama for local model execution.

Used models:

llama3.2:1b
nomic-embed-text

llama3.2:1b is used as a lightweight local generation model from the llama3.2 family. nomic-embed-text is used for local embeddings.

No external LLM API is used.

Setup
1. Install Python dependencies
pip install -r requirements.txt
2. Install Ollama

Download and install Ollama from the official website.

After installation, verify it works:

ollama list
3. Pull local models
ollama pull llama3.2:1b
ollama pull nomic-embed-text
How to run
1. Ingest Wikipedia data
python app/wiki_ingest.py

This creates:

data/raw/person.json
data/raw/place.json
2. Build the vector store
python -m app.main build-index

This creates the local Chroma vector database under:

data/chroma/

The first build may take some time because embeddings are generated locally.

3. Start the chat CLI
python -m app.main chat

To also view retrieved context:

python -m app.main chat --context
Chat commands

Inside the chat:

/exit

exits the chat.

/context on

shows retrieved context.

/context off

hides retrieved context.

/clear

clears the visible terminal spacing.

Example questions

People:

Who was Albert Einstein and what is he known for?
What did Marie Curie discover?
Why is Nikola Tesla famous?
Compare Albert Einstein and Nikola Tesla
What is Frida Kahlo known for?

Places:

Where is the Eiffel Tower located?
Why is the Great Wall of China important?
What is Machu Picchu?
What was the Colosseum used for?
Where is Mount Everest?

Mixed:

Which famous place is located in Turkey?
Which person is associated with electricity?
Compare the Eiffel Tower and the Statue of Liberty

Failure cases:

Who is the president of Mars?
Tell me about a random unknown person John Doe

For these unsupported questions, the system should answer:

I don't know.
Project structure
local-wikipedia-rag/
├── app/
│   ├── main.py
│   ├── wiki_ingest.py
│   ├── chunker.py
│   ├── embedder.py
│   ├── vector_store.py
│   ├── retriever.py
│   ├── generator.py
│   └── chat_cli.py
├── data/
│   ├── raw/
│   └── chroma/
├── README.md
├── product_prd.md
├── recommendation.md
├── requirements.txt
└── demo_link.txt
Limitations

This is a simplified local RAG system for an assignment.

Current limitations:

Wikipedia ingestion is limited to a fixed entity list
retrieval uses simple rule-based query classification
answer quality depends on the small local model
some comparison answers may be shorter than a cloud-based LLM
the system does not use an external API for generation
there is no web frontend; the interface is CLI-based
Notes

The system is intentionally designed to run locally on a laptop. Some steps, especially embedding creation, may take time during the first run. After the vector store is built, chat queries are much faster.


Kaydet.

---

## 4) `product_prd.md` içine bunu koy

```md
# Product PRD — Local Wikipedia RAG Assistant

## 1. Overview

This project is a local Retrieval Augmented Generation system that answers questions about famous people and famous places using Wikipedia data. The system runs fully on localhost and uses local resources for ingestion, embeddings, vector storage, retrieval, and generation.

The system is a simplified ChatGPT-style assistant. It retrieves relevant Wikipedia chunks and uses a local language model to generate grounded answers.

## 2. Goals

- Ingest Wikipedia data for famous people and places
- Store the ingested data locally
- Split documents into smaller chunks
- Generate embeddings locally
- Store embeddings in a local vector database
- Retrieve relevant chunks for a user query
- Generate answers using a local language model
- Avoid external LLM APIs
- Provide a simple chat-style CLI
- Return "I don't know" when the answer is not available in the local data

## 3. Non-Goals

- Building a full web-scale search engine
- Supporting all Wikipedia pages
- Using external LLM APIs
- Building a production-grade UI
- Guaranteeing perfect answer quality
- Real-time Wikipedia synchronization

## 4. Core Features

### 4.1 Ingestion

The system ingests Wikipedia content for at least:

- 20 famous people
- 20 famous places

The required people and places from the assignment are included.

Wikipedia pages are fetched and stored locally as JSON files.

### 4.2 Chunking

The system splits documents into fixed-size overlapping chunks.

The chunking strategy is designed around the assumption that Wikipedia pages can be long. Very long documents are capped to keep local processing practical on a laptop.

### 4.3 Embedding and Storage

The system generates embeddings locally using Ollama and `nomic-embed-text`.

Embeddings are stored in Chroma, a local vector store.

The project uses one vector store with metadata. Each chunk includes metadata such as:

- title
- type
- source
- chunk index

This design was chosen because it simplifies storage and supports metadata filtering for person/place queries.

### 4.4 Retrieval

Given a query, the system retrieves relevant chunks from the local vector store.

The retriever uses simple rule-based logic to determine whether a query is about:

- a person
- a place
- both
- unknown/out of scope

Known entity names are detected directly. For named entities, the system retrieves chunks for that entity. For general queries, it uses vector search with metadata filtering.

### 4.5 Generation

The system uses a local Ollama language model to generate answers.

The answer generation prompt instructs the model to:

- use only retrieved context
- avoid guessing
- avoid outside knowledge
- say "I don't know" when the answer is not in the retrieved data
- keep answers concise and factual

### 4.6 Chat Interface

The project provides a CLI chat interface.

The user can:

- ask questions
- receive generated answers
- optionally view retrieved context
- exit or clear the chat

## 5. Technical Constraints

- Must run fully on localhost
- Must not use external LLM APIs
- Must use a local embedding model
- Must use a local vector store
- Should rely on simple, understandable architecture

## 6. Technology Choices

- Language: Python
- Local model runtime: Ollama
- Generation model: llama3.2:1b
- Embedding model: nomic-embed-text
- Vector store: Chroma
- Interface: CLI
- Data storage: local JSON files and local Chroma persistence

## 7. Architecture

The system is organized into the following modules:

- `wiki_ingest.py`: fetches Wikipedia data
- `chunker.py`: splits documents into chunks
- `embedder.py`: calls Ollama embedding endpoint
- `vector_store.py`: builds and queries Chroma
- `retriever.py`: classifies queries and retrieves context
- `generator.py`: builds prompts and calls the local LLM
- `chat_cli.py`: provides the chat interface
- `main.py`: command entry point

## 8. Success Criteria

The project is successful if:

- Wikipedia data is ingested locally
- at least 20 people and 20 places are stored
- chunks are created from the documents
- embeddings are generated locally
- Chroma stores and retrieves relevant chunks
- the chat interface answers supported questions
- unsupported questions return "I don't know"
- the system can be run by following the README instructions

## 9. Tradeoffs

The project prioritizes local execution and simplicity over maximum answer quality. A smaller local model is used to keep the system runnable on a laptop. Retrieval is improved with metadata and simple entity detection, but it is not a full semantic understanding system.