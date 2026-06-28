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

### Homework 4: Evaluation
The fourth homework focuses on evaluating search and RAG systems.

The implementation covers:
- Generating and using ground truth questions
- Running text search and vector search against the ground truth dataset
- Evaluating retrieval quality with Hit Rate and MRR
- Comparing text search, vector search, and hybrid search
- Using Reciprocal Rank Fusion (RRF) for hybrid search
- Testing different RRF k values and comparing their MRR scores

For Q1, I used Gemini to verify the average input token count for generating questions from the first 3 lesson pages.

Model and Provider for Q1:
- Provider: Google Gemini
- Model: gemini-2.0-flash
- Purpose: Count input tokens for the question generation prompt

The main evaluation code for Q2-Q6 is in homework_04.py.

The Q1 token counting code is in homework_04_q1_count_tokens.py.

Run the main homework:
```bash
uv run python homework_04.py
```

Run the Q1 token counting script:
```bash
uv run python homework_04_q1_count_tokens.py
```
