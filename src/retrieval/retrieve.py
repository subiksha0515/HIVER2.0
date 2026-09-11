"""
Historical Support-Response Retrieval Pipeline.
Performs Top-K dense semantic similarity search over indexed training conversations.
"""

import json
from pathlib import Path
from typing import List, Dict, Any
import numpy as np
import joblib


class ResponseRetriever:
    """Vector Retrieval System for searching historical customer support cases."""

    def __init__(self, index_dir: str = "models/retrieval_index"):
        self.index_dir = Path(index_dir)
        self.vectorizer_file = self.index_dir / "vectorizer.joblib"
        self.svd_file = self.index_dir / "svd.joblib"
        self.nn_file = self.index_dir / "nn_model.joblib"
        self.embeds_file = self.index_dir / "embeddings.npy"
        self.meta_file = self.index_dir / "metadata.json"
        self.config_file = self.index_dir / "config.json"

        if not self.vectorizer_file.exists() or not self.meta_file.exists():
            raise FileNotFoundError(
                f"Retrieval index files not found in '{index_dir}'. Please run `python -m src.retrieval.index` first."
            )

        with open(self.config_file, "r", encoding="utf-8") as f:
            self.config = json.load(f)

        print("Loading vectorizer, SVD model, and NN index...")
        self.vectorizer = joblib.load(self.vectorizer_file)
        self.svd = joblib.load(self.svd_file)
        self.nn_model = joblib.load(self.nn_file)
        self.embeddings = np.load(self.embeds_file)

        print(f"Loading metadata ({self.config.get('total_examples', 0):,} records)...")
        with open(self.meta_file, "r", encoding="utf-8") as f:
            self.metadata = json.load(f)

    def retrieve(self, query_text: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieves top_k similar historical cases for a given query_text.
        Returns: List of dicts containing:
          - historical_customer_message
          - historical_brand_response
          - similarity_score (cosine similarity 0..1)
          - intent
          - conversation_id
          - context
        """
        if top_k <= 0:
            return []

        tfidf_vec = self.vectorizer.transform([query_text])
        dense_vec = self.svd.transform(tfidf_vec)
        norm = np.linalg.norm(dense_vec)
        if norm > 0:
            dense_vec = dense_vec / norm

        distances, indices = self.nn_model.kneighbors(dense_vec, n_neighbors=top_k)

        results = []
        for rank in range(top_k):
            idx = int(indices[0][rank])
            dist = float(distances[0][rank])
            similarity = round(max(0.0, 1.0 - dist), 4)

            if idx < 0 or idx >= len(self.metadata):
                continue

            meta = self.metadata[idx]
            results.append({
                "rank": rank + 1,
                "similarity_score": similarity,
                "historical_customer_message": meta["customer_message"],
                "historical_brand_response": meta["brand_response"],
                "intent": meta["intent"],
                "conversation_id": meta["conversation_id"],
                "context": meta.get("context", ""),
                "timestamp": meta.get("timestamp", "")
            })

        return results


def main():
    retriever = ResponseRetriever()
    test_query = "Where is my package? The tracking number is not updating!"
    print(f"\nTest Query: '{test_query}'")
    matches = retriever.retrieve(test_query, top_k=3)
    for m in matches:
        print(f"\n[Rank {m['rank']}] Similarity: {m['similarity_score']:.4f} | Intent: {m['intent']}")
        print(f"  Customer: {m['historical_customer_message']}")
        print(f"  Response: {m['historical_brand_response']}")


if __name__ == "__main__":
    main()
