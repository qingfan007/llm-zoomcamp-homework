import pandas as pd
import minsearch
import numpy as np

from gitsource import GithubRepositoryDataReader, chunk_documents
from embedder import Embedder

"""
Homework 4: Evaluation

Q1 is verified separately in:
    homework_04_q1_count_tokens.py

This file contains the code for Q2-Q6:
- text_search first result
- vector_search first result
- Hit Rate / MRR evaluation
- hybrid_search RRF k comparison
"""
def build_data():
    reader = GithubRepositoryDataReader(
        repo_owner="DataTalksClub",
        repo_name="llm-zoomcamp",
        commit_id="8c1834d",
        allowed_extensions={"md"},
        filename_filter=lambda path: "/lessons/" in path,
    )

    documents = [file.parse() for file in reader.read()]
    chunks = chunk_documents(documents, size=2000, step=1000)

    print(f"Documents: {len(documents)}")
    print(f"Chunks: {len(chunks)}")

    return documents, chunks

def build_text_index(chunks):
    index = minsearch.Index(
        text_fields=["content"],
        keyword_fields=["filename"],
    )

    index.fit(chunks)
    return index

def build_vector_index(chunks):
    embedder = Embedder()

    for chunk in chunks:
        chunk["embedding"] = embedder.encode(chunk["content"])

    embeddings = np.array([chunk["embedding"] for chunk in chunks])

    return embedder, embeddings

def cosine_similarity(a, b):
    a_norm = np.linalg.norm(a)
    b_norm = np.linalg.norm(b)
    if a_norm == 0 or b_norm == 0:
        return 0.0

    return np.dot(a, b) / (a_norm * b_norm)

def main():
    documents, chunks = build_data()

    ground_truth_df = pd.read_csv("ground-truth.csv")
    ground_truth = ground_truth_df.to_dict(orient="records")

    print(f"Ground truth records: {len(ground_truth)}")
    print("First ground truth question:")
    print(ground_truth[0])

    text_index = build_text_index(chunks)
    embedder, embeddings = build_vector_index(chunks)

    def text_search(query, num_results=5):
        return text_index.search(
            query=query,
            filter_dict={},
            boost_dict={},
            num_results=num_results,
        )

    def vector_search(query, num_results=5):
        query_embedding = embedder.encode(query)
        scores = embeddings @ query_embedding
        idx = np.argsort(scores)[::-1][:num_results]
        return [chunks[i] for i in idx]

    q = ground_truth[0]["question"]

    print("\nQ2 text_search first result:")
    text_results = text_search(q)
    print(text_results[0]["filename"])

    print("\nQ3 vector_search first result:")
    vector_results = vector_search(q)
    print(vector_results[0]["filename"])


    def hit_rate(relevance_total):
        cnt = 0
        for line in relevance_total:
            if True in line:
                cnt += 1
        return cnt / len(relevance_total)
    
    def mrr(relevance_total):
        total_score = 0
        for line in relevance_total:
            for rank, is_relevant in enumerate(line):
                if is_relevant:
                    total_score += 1 / (rank + 1)
                    break
        return total_score / len(relevance_total)
    
    def evaluate(ground_truth, search_function):
        relevance_total = []
        for record in ground_truth:
            query = record["question"]
            expected_filename = record["filename"]
            results = search_function(query)
            relevance = [
                doc["filename"] == expected_filename
                for doc in results
            ]
            relevance_total.append(relevance)

        return {
         "hit_rate": hit_rate(relevance_total),
         "mrr": mrr(relevance_total)
        }
    
    print("\nQ4 text_search evaluation:")
    text_metrics = evaluate(ground_truth, text_search)
    print(text_metrics)

    print("\nQ5 vector_search evaluation:")
    vector_metrics = evaluate(ground_truth, vector_search)
    print(vector_metrics)

    def hybrid_search(query, num_results=5, k=60):
        text_results = text_search(query, num_results=num_results)
        vector_results = vector_search(query, num_results=num_results)

        scores = {}
        documents = {}

        for rank, doc in enumerate(text_results):
            doc_id = (doc["filename"], doc["start"])
            if doc_id not in scores:
                scores[doc_id] = 0.0
                documents[doc_id] = doc
            scores[doc_id] += 1 / (k + rank + 1)
        for rank, doc in enumerate(vector_results):
            doc_id = (doc["filename"], doc["start"])
            if doc_id not in scores:
                scores[doc_id] = 0.0
                documents[doc_id] = doc
            scores[doc_id] += 1 / (k + rank + 1)
        ranked_doc_ids = sorted(scores, key=scores.get, reverse=True)
        return [documents[doc_id] for doc_id in ranked_doc_ids[:num_results]]
    
    print("\nQ6 hybrid_search evaluation:")
    for k in [1, 50, 100, 200]:
        def search_fn(query, k=k):
            return hybrid_search(query, num_results=5, k=k)
        metrics = evaluate(ground_truth, search_fn)
        print(f"k={k}: {metrics}")
    

if __name__ == "__main__":
    main()

