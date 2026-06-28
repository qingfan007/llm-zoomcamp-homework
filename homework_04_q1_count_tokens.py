import os
import json

from google import genai
from dotenv import load_dotenv
from gitsource import GithubRepositoryDataReader

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

data_gen_instructions = """
You emulate a student who is taking our LLM course.
You are given one lesson page from the course.
Formulate 5 questions this student might ask that are answered by this page.
Rules:
- The page should contain the answer to each question.
- Make the questions complete and not too short.
- Use as few words as possible from the page; don't copy its phrasing.
- The questions should resemble how people actually ask things online:
  not too formal, not too short, not too long.
- Ask about the content of the lesson, not about its formatting or filename.
""".strip()

reader = GithubRepositoryDataReader(
    repo_owner="DataTalksClub",
    repo_name="llm-zoomcamp",
    commit_id="8c1834d",
    allowed_extensions={"md"},
    filename_filter=lambda path: "/lessons/" in path,
)

documents = [file.parse() for file in reader.read()]

target_files = [
    "01-agentic-rag/lessons/01-intro.md",
    "01-agentic-rag/lessons/02-environment.md",
    "01-agentic-rag/lessons/03-rag.md",
]

selected_docs = [
    doc for doc in documents
    if doc["filename"] in target_files
]

selected_docs = sorted(
    selected_docs,
    key=lambda doc: target_files.index(doc["filename"])
)

token_counts = []

for doc in selected_docs:
    user_prompt = json.dumps(
        {
            "filename": doc["filename"],
            "content": doc["content"],
        },
        ensure_ascii=False,
    )

    full_prompt = data_gen_instructions + "\n\n" + user_prompt

    result = client.models.count_tokens(
        model="gemini-2.0-flash",
        contents=full_prompt,
    )

    input_tokens = result.total_tokens
    token_counts.append(input_tokens)

    print(doc["filename"])
    print("input tokens:", input_tokens)
    print()

average = sum(token_counts) / len(token_counts)

print("Token counts:", token_counts)
print("Average input tokens:", average)