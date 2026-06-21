from gitsource import GithubRepositoryDataReader, chunk_documents
import minsearch
from openai import OpenAI
import json


# ---------------------------------------------------------
# Q1: Load all lesson pages
# ---------------------------------------------------------

reader = GithubRepositoryDataReader(
    repo_owner="DataTalksClub",
    repo_name="llm-zoomcamp",
    commit_id="8c1834d",
    allowed_extensions={"md"},
    filename_filter=lambda path: "/lessons/" in path,
)

files = reader.read()

documents = []

for file in files:
    document = file.parse()
    documents.append(document)

print(f"Number of lesson pages: {len(documents)}")

print("\nFirst three documents:")
for document in documents[:3]:
    print(document["filename"])


# ---------------------------------------------------------
# Q2: Indexing and searching
# ---------------------------------------------------------

index = minsearch.Index(
    text_fields=["content"],
    keyword_fields=["filename"],
)

index.fit(documents)

query = "How does the agentic loop keep calling the model until it stops?"

results = index.search(
    query=query,
    num_results=5,
)

print("\nTop search results:")
for result in results:
    print(result["filename"])


# ---------------------------------------------------------
# Ollama client
# ---------------------------------------------------------

client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama",
)


# ---------------------------------------------------------
# Q3: RAG without chunking
#
# Already completed.
# Keep this section commented to avoid running it again.
# ---------------------------------------------------------

search_results = index.search(
    query=query,
    num_results=5,
)

context = "\n\n".join(
    f"Filename: {result['filename']}\n"
    f"Content: {result['content']}"
    for result in search_results
)

prompt = f"""
You're a course teaching assistant.

Answer the QUESTION using only the information from the CONTEXT.

QUESTION:
{query}

CONTEXT:
{context}
""".strip()

# response = client.chat.completions.create(
#     model="llama3.1:8b",
#     messages=[
#         {
#             "role": "user",
#             "content": prompt,
#         }
#     ],
# )

# print("\nRAG answer:")
# print(response.choices[0].message.content)

# print("\nInput tokens:")
# print(response.usage.prompt_tokens)


# ---------------------------------------------------------
# Q4: Chunking
# ---------------------------------------------------------

chunks = chunk_documents(
    documents,
    size=2000,
    step=1000,
)

print("\nNumber of chunks:")
print(len(chunks))

print("\nFirst chunk:")
print(chunks[0]["filename"])
print(chunks[0]["start"])
print(chunks[0]["content"][:300])


# ---------------------------------------------------------
# Q5: RAG with chunking
#
# Already completed.
# Keep the LLM call commented to avoid running it again.
# ---------------------------------------------------------

chunk_index = minsearch.Index(
    text_fields=["content"],
    keyword_fields=["filename"],
)

chunk_index.fit(chunks)

chunk_search_results = chunk_index.search(
    query=query,
    num_results=5,
)

print("\nTop chunk search results:")
for result in chunk_search_results:
    print(result["filename"], result["start"])

chunk_context = "\n\n".join(
    f"Filename: {result['filename']}\n"
    f"Content: {result['content']}"
    for result in chunk_search_results
)

chunk_prompt = f"""
You're a course teaching assistant.

Answer the QUESTION using only the information from the CONTEXT.

QUESTION:
{query}

CONTEXT:
{chunk_context}
""".strip()

# chunk_response = client.chat.completions.create(
#     model="llama3.1:8b",
#     messages=[
#         {
#             "role": "user",
#             "content": chunk_prompt,
#         }
#     ],
# )

# print("\nChunked RAG answer:")
# print(chunk_response.choices[0].message.content)

# print("\nChunked input tokens:")
# print(chunk_response.usage.prompt_tokens)


# ---------------------------------------------------------
# Q6: Turn the chunked RAG into an agent
# ---------------------------------------------------------

def search_course(query: str) -> list[dict]:
    """
    Search the LLM Zoomcamp course lessons for information
    relevant to the given query.
    """

    results = chunk_index.search(
        query=query,
        num_results=3,
    )

    return [
        {
            "filename": result["filename"],
            "start": result["start"],
            "content": result["content"][:1200],
        }
        for result in results
    ]


tools = [
    {
        "type": "function",
        "function": {
            "name": "search_course",
            "description": (
                "Search the LLM Zoomcamp course lessons for information "
                "needed to answer a student's question."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": (
                            "Keywords or a short question used to search "
                            "the course lessons."
                        ),
                    }
                },
                "required": ["query"],
            },
        },
    }
]


messages = [
    {
        "role": "system",
        "content": (
            "You are a course teaching assistant. "
            "You must use the search_course tool before answering. "
            "Call the tool multiple times with different search queries. "
            "Do not describe or simulate tool calls in plain text. "
            "Use actual function calls only. "
            "After gathering enough information, answer the student's question."
        ),
    },
    {
        "role": "user",
        "content": (
            "How does the agentic loop work, "
            "and how is it different from plain RAG?"
        ),
    },
]


search_count = 0

for iteration in range(10):
    print(f"\nAgent iteration: {iteration + 1}")

    response = client.chat.completions.create(
        model="qwen3:8b",
        messages=messages,
        tools=tools,
        tool_choice="required" if search_count < 4 else "auto",
        temperature=0,
    )

    assistant_message = response.choices[0].message
    messages.append(assistant_message)

    # If there are no tool calls, the agent has finished.
    if not assistant_message.tool_calls:
        print("\nAgent answer:")
        print(assistant_message.content)
        break

    for tool_call in assistant_message.tool_calls:
        if tool_call.function.name != "search_course":
            continue

        try:
            arguments = json.loads(tool_call.function.arguments)
        except json.JSONDecodeError as error:
            print(f"Could not parse tool arguments: {error}")
            continue

        search_query = arguments.get("query")

        if not search_query:
            print("Tool call did not contain a query.")
            continue

        search_count += 1

        print(f"\nSearch call {search_count}: {search_query}")

        search_results = search_course(search_query)

        messages.append(
            {
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(
                    search_results,
                    ensure_ascii=False,
                ),
            }
        )

else:
    print("\nAgent stopped because it reached the iteration limit.")

print(f"\nTotal search calls: {search_count}")