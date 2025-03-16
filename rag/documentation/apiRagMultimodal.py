# LlamaIndex Embeddings API Guide

#A guide to use the Modal-deployed embeddings API for encoding both queries and documents (images).

import requests
import json
import numpy as np
from pathlib import Path

# Base URL for the API
BASE_URL = "https://lmspaul--llamaindex-embeddings-fast-api.modal.run"

# Helper functions for API calls
def encode_queries(queries, dimension=1536):
    url = f"{BASE_URL}/encode_queries"

    payload = {
        "queries": queries
    }

    response = requests.post(
        url,
        json=payload,
        params={"dimension": dimension}
    )

    if response.status_code == 200:
        return response.json()["embeddings"]
    else:
        raise Exception(f"Error: {response.status_code}, {response.text}")

def encode_documents(image_paths, dimension=1536):
    url = f"{BASE_URL}/encode_documents"

    files = []
    for path in image_paths:
        files.append(
            ('files', (Path(path).name, open(path, 'rb'), 'image/jpeg'))
        )

    response = requests.post(
        url,
        files=files,
        params={"dimension": dimension}
    )

    if response.status_code == 200:
        return response.json()["embeddings"]
    else:
        raise Exception(f"Error: {response.status_code}, {response.text}")

def compute_similarity(query_embedding, doc_embedding):
    return np.dot(query_embedding, doc_embedding)

# Example usage
def main():
    # Example queries and documents
    # Only send one query at a time otherwise it will throw an error
    queries = [
        "Document qui présente comment l'hydrogène est produit"
    ]
    image_paths = ["path/to/image1.jpg"]

    try:
        # Get embeddings
        print("Getting query embeddings...")
        query_embeddings = encode_queries(queries)
        print(f"Query embeddings shape: {len(query_embeddings)}x{len(query_embeddings[0])}")

        print("\\nGetting document embeddings...")
        doc_embeddings = encode_documents(image_paths)
        print(f"Document embeddings shape: {len(doc_embeddings)}x{len(doc_embeddings[0])}")

        # Compute similarities
        print("\\nComputing similarities...")
        for i, query in enumerate(queries):
            for j, doc_path in enumerate(image_paths):
                similarity = compute_similarity(
                    query_embeddings[i],
                    doc_embeddings[j]
                )
                print(f"\\nQuery: '{query}'")
                print(f"Document: {doc_path}")
                print(f"Similarity score: {similarity:.4f}")

    except Exception as e:
        print(f"Error occurred: {str(e)}")

if __name__ == "__main__":
    main()