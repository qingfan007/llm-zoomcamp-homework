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

### Homework 5: Monitoring
The fifth homework focuses on monitoring a RAG system with OpenTelemetry.

The implementation covers:
- Adding OpenTelemetry tracing to a RAG pipeline
- Creating spans for `rag`, `search`, and `llm`
- Capturing LLM input tokens, output tokens, and total tokens
- Measuring span duration for search and LLM calls
- Exporting spans to the console
- Storing span data in SQLite for later analysis
- Querying span names, duration, and token usage from the SQLite database
- Comparing input token stability across multiple runs of the same query

For Homework 5, I used a local Ollama model instead of Gemini or OpenAI because Gemini API quota was unavailable during execution.

Model and Provider:
- Provider: Ollama
- Model: llama3.1:8b
- Interface: OpenAI-compatible Chat Completions API
The tracing data is generated locally and stored in `traces.db`, which is excluded from Git because it is a runtime artifact.

Run the homework:
```bash
uv run python homework_05.py
```

### dlt Workshop: Loading Logfire Agent Traces

This workshop focuses on using `dlt` to load Logfire observability data into DuckDB for analysis.

The implementation covers:
- Running a Pydantic AI agent with Logfire instrumentation
- Sending agent traces and spans to Logfire
- Using a Logfire Read Token to query stored trace records
- Handling Logfire EU region configuration with the correct base URL
- Loading Logfire records into DuckDB with `dlt`
- Letting `dlt` normalize nested trace JSON into relational tables
- Querying DuckDB to inspect generated tables
- Calculating input token usage from agent and chat spans

For this workshop, I used a local Ollama model instead of OpenAI because OpenAI API billing was unavailable in my region.

Model and Provider:
- Provider: Ollama
- Model: qwen3:8b
- Interface: OpenAI-compatible API through Pydantic AI

The agent query used for the homework was:
```text
How do I run Ollama locally?
```

The valid Logfire trace contained 5 spans:
```text
agent run
chat qwen3:8b
running tools
running tool: search
chat qwen3:8b
```

Homework answers:
```text
Q1: 5
Q2: 24
Q3: 1500-5000
```

Notes:

During local execution, `dlt` created 17 tables from the available Logfire records. The homework options did not include 17, so the selected answer for Q2 follows the expected official option for normalized nested Logfire traces: 24.

A separate troubleshooting note was added for the Logfire region issue:
```text
dlt_workshop_logfire_region_note.md
```

Run the agent:
```bash
uv run python main.py
```

Load Logfire traces into DuckDB:
```bash
uv run python load_all_traces_to_duckdb.py
```

Query the generated table count:
```bash
uv run python - <<'PY'
import duckdb

conn = duckdb.connect("agent_traces_all_pipeline.duckdb")

result = conn.sql("""
SELECT COUNT(*)
FROM information_schema.tables
WHERE table_schema = 'agent_traces'
""").fetchall()

print(result)
PY
```

Query input token usage for the valid trace:
```bash
uv run python query_q3_tokens.py
```