"""Homework 5: Monitoring

This version uses a local Ollama model through the
OpenAI-compatible Chat Completions API.

The monitoring and tracing logic will be added after
the base RAG pipeline is confirmed to work.
"""

from openai import OpenAI

from gitsource import GithubRepositoryDataReader
from minsearch import Index

from rag_helper_hw5 import RAGBase

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    ConsoleSpanExporter,
    SimpleSpanProcessor,
)
import sqlite3
from datetime import datetime

class SQLiteSpanExporter:
    """Simple OpenTelemetry span exporter that writes spans to SQLite."""

    def __init__(self, db_path="traces.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS spans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                trace_id TEXT,
                span_id TEXT,
                parent_id TEXT,
                name TEXT,
                start_time TEXT,
                end_time TEXT,
                duration_ms REAL,
                model TEXT,
                input_tokens INTEGER,
                output_tokens INTEGER,
                total_tokens INTEGER
            )
        """)

        conn.commit()
        conn.close()

    def export(self, spans):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        for span in spans:
            context = span.get_span_context()

            trace_id = format(context.trace_id, "032x")
            span_id = format(context.span_id, "016x")

            parent_id = None
            if span.parent:
                parent_id = format(span.parent.span_id, "016x")

            start_time = datetime.fromtimestamp(
                span.start_time / 1_000_000_000
            ).isoformat()

            end_time = datetime.fromtimestamp(
                span.end_time / 1_000_000_000
            ).isoformat()

            duration_ms = (
                span.end_time - span.start_time
            ) / 1_000_000

            attrs = span.attributes or {}

            cursor.execute(
                """
                INSERT INTO spans (
                    trace_id,
                    span_id,
                    parent_id,
                    name,
                    start_time,
                    end_time,
                    duration_ms,
                    model,
                    input_tokens,
                    output_tokens,
                    total_tokens
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    trace_id,
                    span_id,
                    parent_id,
                    span.name,
                    start_time,
                    end_time,
                    duration_ms,
                    attrs.get("model"),
                    attrs.get("input_tokens"),
                    attrs.get("output_tokens"),
                    attrs.get("total_tokens"),
                ),
            )

        conn.commit()
        conn.close()

        return None

    def shutdown(self):
        return None

    def force_flush(self, timeout_millis=30000):
        return True


provider = TracerProvider()
provider.add_span_processor(
    SimpleSpanProcessor(ConsoleSpanExporter())
)

provider.add_span_processor(
    SimpleSpanProcessor(SQLiteSpanExporter("traces.db"))
)

trace.set_tracer_provider(provider)

tracer = trace.get_tracer("llm-zoomcamp-monitoring")


COMMIT = "8c1834d"

# Load the same course lesson pages used in the previous homework.
reader = GithubRepositoryDataReader(
    repo_owner="DataTalksClub",
    repo_name="llm-zoomcamp",
    commit_id=COMMIT,
    allowed_extensions={"md"},
    filename_filter=lambda path: "/lessons/" in path,
)

documents = [file.parse() for file in reader.read()]

# Build the keyword-search index.
index = Index(
    text_fields=["content"],
    keyword_fields=["filename"],
)
index.fit(documents)


class TracedOllamaRAG(RAGBase):
    """RAG implementation with OpenTelemetry spans."""

    def search(self, query, num_results=5):
        with tracer.start_as_current_span("search") as span:
            span.set_attribute("query", query)
            span.set_attribute("num_results", num_results)

            results = self.index.search(
                query,
                num_results=num_results,
            )

            span.set_attribute("results_count", len(results))

            return results

    def llm(self, prompt):
        with tracer.start_as_current_span("llm") as span:
            response = self.llm_client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": self.instructions + "\nAnswer briefly in 3-5 sentences.",
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    },
                ],
                temperature=0,
                max_tokens=200,
            )

            span.set_attribute("model", self.model)

            usage = response.usage
            if usage is not None:
                span.set_attribute("input_tokens", usage.prompt_tokens)
                span.set_attribute("output_tokens", usage.completion_tokens)
                span.set_attribute("total_tokens", usage.total_tokens)

            return response

    def rag(self, query):
        with tracer.start_as_current_span("rag") as span:
            span.set_attribute("query", query)

            search_results = self.search(query)
            prompt = self.build_prompt(query, search_results)
            response = self.llm(prompt)

            answer = response.choices[0].message.content

            span.set_attribute("answer_length", len(answer or ""))

            return answer


client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama",
)

rag = TracedOllamaRAG(
    index=index,
    llm_client=client,
    model="llama3.1:8b",
)


if __name__ == "__main__":
    query = (
        "How does the agentic loop keep calling "
        "the model until it stops?"
    )

    answer = rag.rag(query)

    print(f"Documents loaded: {len(documents)}")
    for i in range(4):
       print(f"\nRun {i + 1}")
       answer = rag.rag(query)
       print(answer[:200])