from embedder import Embedder
import numpy as np
from gitsource import GithubRepositoryDataReader, chunk_documents
from tqdm import tqdm
from minsearch import VectorSearch
from minsearch import Index

# ---------------------------------------------------------
# Q1: Embedding a query
# ---------------------------------------------------------

embedder = Embedder()
query = "How does approximate nearest neighbor search work?"
v = embedder.encode(query)

print("Embedding length:", len(v))
print("First value:", v[0])

# ---------------------------------------------------------
# Q2: Cosine similarity
# ---------------------------------------------------------
# reader = GithubRepositoryDataReader(
#     repo_owner="DataTalksClub",
#     repo_name="llm-zoomcamp",
#     commit_id="8c1834d",
#     allowed_extensions={"md"},
#     filename_filter=lambda path: path == "02-vector-search/lessons/07-sqlitesearch-vector.md",
# )

# files = reader.read()

# document = files[0].parse()
# content = document["content"]

# doc_vector = embedder.encode(content)
# similarity = np.dot(v,doc_vector)

# print("\nQ2")
# print("Document filename:", document["filename"])
# print("Cosine similarity:", similarity)

# ---------------------------------------------------------
# Q3: Chunking and search by hand
# ---------------------------------------------------------

readers = GithubRepositoryDataReader(
    repo_owner="DataTalksClub",
    repo_name="llm-zoomcamp",
    commit_id="8c1834d",
    allowed_extensions={"md"},
    filename_filter=lambda path: "/lessons/" in path,
)

documents = [file.parse() for file in readers.read()]
chunks = chunk_documents(
    documents,
    size=2000,
    step=1000,
)

print("\nQ3")
print("Number of documents:", len(documents))
print("Number of chunks:", len(chunks))

chunk_contents = [chunk["content"] for chunk in chunks]
chunk_vectors = []

for content in tqdm(chunk_contents):
    chunk_vector = embedder.encode(content)
    chunk_vectors.append(chunk_vector)

X = np.array(chunk_vectors)

scores = X.dot(v)

best_index = np.argmax(scores)
best_chunk = chunks[best_index]
best_score = scores[best_index]

print("Best score:", best_score)
print("Best filename:", best_chunk["filename"])
print("Best start:", best_chunk["start"])

# ---------------------------------------------------------
# Q4: Vector search with minsearch
# ---------------------------------------------------------

print("\nQ4")

vector_index = VectorSearch(
    keyword_fields=["filename"],
)

vector_index.fit(
    vectors=X,
    payload=chunks,
)

q4_query = "What metric do we use to evaluate a search engine?"
q4_query_vector = embedder.encode(q4_query)

q4_results = vector_index.search(
    query_vector=q4_query_vector,
    num_results=5,
)

print("Top vector search results:")

for result in q4_results:
    print(result["filename"], result["start"])

# ---------------------------------------------------------
# Q5: Text search vs vector search
# ---------------------------------------------------------
print("\nQ5")

q5_query = "How do I store vectors in PostgreSQL?"
q5_query_vector = embedder.encode(q5_query)

q5_vector_results = vector_index.search(
    query_vector=q5_query_vector,
    num_results=5,
)

text_index = Index(
    text_fields=["content"],
    keyword_fields=["filename"],
)

text_index.fit(chunks)

q5_text_results = text_index.search(
    query=q5_query,
    num_results=5,
)

print("Vector search results:")

for result in q5_vector_results:
    print(result["filename"], result["start"])

print("\nText search results:")
for result in q5_text_results:
    print(result["filename"], result["start"])

vector_files = {result["filename"] for result in q5_vector_results}
text_files = {result["filename"] for result in q5_text_results}

print("\nFiles in vector results but not in text results:")
for filename in vector_files - text_files:
    print(filename)


# ---------------------------------------------------------
# Q6: Hybrid search
# ---------------------------------------------------------
print("\nQ6")

q6_query = "How does the agentic loop work?"
q6_query_vector = embedder.encode(q6_query)

q6_vector_results = vector_index.search(
    query_vector=q6_query_vector,
    num_results=10,
)

q6_text_results = text_index.search(
    query=q6_query,
    num_results=10,
)

def rrf_score(rank: int, k: int = 60) -> float:
    return 1 / (k + rank)

scores = {}

for rank, result in enumerate(q6_vector_results, start=1):
    key = (result["filename"], result["start"])
    scores[key] = scores.get(key, 0) + rrf_score(rank)

for rank, result in enumerate(q6_text_results, start=1):
    key = (result["filename"], result["start"])
    scores[key] = scores.get(key, 0) + rrf_score(rank)

ranked_results = sorted(
    scores.items(),
    key=lambda item: item[1],
    reverse=True,
)

print("Vector search results:")
for result in q6_vector_results:
    print(result["filename"], result["start"])

print("\nText search results:")
for result in q6_text_results:
    print(result["filename"], result["start"])

print("\nHybrid search results:")
for (filename, start), score in ranked_results[:5]:
    print(filename, start, score)

print("\nBest hybrid result:")
print(ranked_results[0][0][0])
