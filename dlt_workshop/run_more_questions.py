import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(".env"), override=True)

import logfire

logfire.configure(
    token=os.getenv("LOGFIRE_TOKEN"),
    base_url=os.getenv("LOGFIRE_BASE_URL"),
)

from agent import faq_agent, SearchDeps
from ingest import build_index, load_faq_data


def main():
    documents = load_faq_data()
    index = build_index(documents)
    deps = SearchDeps(index=index)

    questions = [
        "How do I run Ollama locally?",
        "How do I install Ollama?",
        "Can I run the course locally instead of Codespaces?",
        "How do I use OpenAI API in the course?",
        "What should I do if I just discovered the course?",
    ]

    for question in questions:
        print("\nQUESTION:", question)
        result = faq_agent.run_sync(question, deps=deps)
        print("ANSWER:", result.output[:500])


if __name__ == "__main__":
    main()