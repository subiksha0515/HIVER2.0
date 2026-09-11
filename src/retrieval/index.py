"""
Historical Support-Response Vector Indexing System.
Indexes historical training customer-support conversations using Dense LSA + TF-IDF Vector Indexing.
STRICT LEAKAGE PREVENTION: Only indexes data/processed/train.jsonl.
"""

import json
import time
from pathlib import Path
from typing import List, Dict, Any
import numpy as np
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.neighbors import NearestNeighbors


def build_historical_response_index(
    train_path: str = "data/processed/train.jsonl",
    output_dir: str = "models/retrieval_index",
    n_components: int = 300
):
    start_time = time.time()
    print("=" * 70)
    print("STARTING HISTORICAL SUPPORT-RESPONSE VECTOR INDEXING")
    print("=" * 70)

    print(f"\n1. Loading historical training conversations from {train_path}...")
    metadata = []
    texts_to_encode = []

    with open(train_path, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            rec = json.loads(line)

            cust_msg = rec.get("customer_message", "").strip()
            brand_resp = rec.get("brand_response", "").strip()

            if not cust_msg or not brand_resp:
                continue

            context_str = f"Brand: {rec.get('brand', 'AmazonHelp')} | Turns: {rec.get('turns', 1)}"

            texts_to_encode.append(cust_msg)
            metadata.append({
                "conversation_id": rec.get("conversation_id", ""),
                "customer_message": cust_msg,
                "brand_response": brand_resp,
                "intent": rec.get("intent", "OTHER / UNKNOWN"),
                "turns": rec.get("turns", 1),
                "context": context_str,
                "timestamp": rec.get("timestamp", "")
            })

    total_examples = len(texts_to_encode)
    print(f"   Total valid training examples to index: {total_examples:,}")

    print(f"\n2. Extracting TF-IDF features and fitting TruncatedSVD ({n_components}d dense embeddings)...")
    vectorizer = TfidfVectorizer(ngram_range=(1, 2), min_df=2, max_features=35000, sublinear_tf=True)
    tfidf_mat = vectorizer.fit_transform(texts_to_encode)

    svd = TruncatedSVD(n_components=n_components, random_state=42)
    dense_embeds = svd.fit_transform(tfidf_mat)

    # Normalize vectors for cosine similarity
    norms = np.linalg.norm(dense_embeds, axis=1, keepdims=True)
    norms[norms == 0] = 1e-10
    dense_embeds = (dense_embeds / norms).astype("float32")

    print("\n3. Building Nearest Neighbors Vector Index...")
    nn_model = NearestNeighbors(n_neighbors=10, metric="cosine", algorithm="brute")
    nn_model.fit(dense_embeds)

    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    print(f"\n4. Persisting vector index and metadata to {out_path}...")
    joblib.dump(vectorizer, out_path / "vectorizer.joblib")
    joblib.dump(svd, out_path / "svd.joblib")
    joblib.dump(nn_model, out_path / "nn_model.joblib")
    np.save(out_path / "embeddings.npy", dense_embeds)

    with open(out_path / "metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

    with open(out_path / "config.json", "w", encoding="utf-8") as f:
        json.dump({
            "embedding_type": f"TF-IDF + TruncatedSVD ({n_components}d)",
            "total_examples": total_examples,
            "dimension": n_components,
            "source_path": train_path,
            "indexed_at": time.strftime("%Y-%m-%d %H:%M:%S")
        }, f, indent=2)

    elapsed = round(time.time() - start_time, 2)
    print("\n" + "=" * 70)
    print(f"HISTORICAL RESPONSE RETRIEVAL INDEX BUILT SUCCESSFULLY IN {elapsed} SECONDS")
    print(f"Saved artifacts in {out_path}:")
    print("  - vectorizer.joblib")
    print("  - svd.joblib")
    print("  - nn_model.joblib")
    print("  - embeddings.npy")
    print("  - metadata.json")
    print("=" * 70)


if __name__ == "__main__":
    build_historical_response_index()
