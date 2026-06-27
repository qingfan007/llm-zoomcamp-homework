## LLM Zoomcamp Homework

This repository contains my homework and project work for the DataTalksClub LLM Zoomcamp.

### Homework 1: Agentic RAG

The first homework builds a Retrieval-Augmented Generation system using the LLM Zoomcamp lesson materials as the knowledge base.

The implementation covers:
- Loading lesson documents from GitHub
- Indexing and keyword search with minsearch
- Building a basic RAG pipeline
- Splitting documents into overlapping chunks
- Comparing RAG input size before and after chunking
- Turning the search workflow into an agent with tool calling

Model and Provider

For Homework 1, I used a local model through Ollama:
- Provider: Ollama
- Model: qwen3:8b
- Interface: OpenAI-compatible Chat Completions API

OpenAI API billing is not available for my current billing region, so I used a local model to complete and understand the same RAG and agent workflow.

Because tokenization and tool-calling behavior vary between models, some runtime values may differ slightly from the reference results.

Run the homework:
```bash
uv run python homework_01.py
```

### Homework 2: Vector Search
The second homework focuses on vector search for RAG retrieval.

The implementation covers:
- Creating embeddings for queries and lesson documents
- Computing cosine similarity between embeddings
- Splitting lesson documents into chunks
- Performing vector search manually with NumPy
- Using minsearch for vector search
- Comparing text search and vector search results
- Combining text search and vector search with hybrid search using RRF

For Homework 2, I used the course-provided ONNX embedder based on Xenova/all-MiniLM-L6-v2.

Run the homework:
```bash
uv run python homework_02.py
```