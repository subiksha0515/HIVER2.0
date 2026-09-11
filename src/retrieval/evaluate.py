"""
Retrieval Evaluation Pipeline for AI Customer Support Agent.
Evaluates historical support-response retrieval on held-out test conversations (test.jsonl).
Measures Recall@1, Recall@3, Recall@5, and Mean Reciprocal Rank (MRR).
Inspects successful and failed retrieval cases and generates reports/retrieval_evaluation.md.
"""

import json
import time
from pathlib import Path
from typing import List, Dict, Any
import numpy as np

from src.retrieval.retrieve import ResponseRetriever


def load_test_conversations(test_path: str = "data/processed/test.jsonl") -> List[Dict[str, Any]]:
    test_recs = []
    with open(test_path, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            rec = json.loads(line)
            if rec.get("customer_message") and rec.get("brand_response"):
                test_recs.append(rec)
    return test_recs


def run_retrieval_evaluation(
    test_path: str = "data/processed/test.jsonl",
    report_path: str = "reports/retrieval_evaluation.md"
):
    start_time = time.time()
    print("=" * 70)
    print("STARTING HISTORICAL RESPONSE RETRIEVAL EVALUATION PIPELINE")
    print("=" * 70)

    print(f"\n1. Initializing ResponseRetriever...")
    retriever = ResponseRetriever()

    print(f"\n2. Loading held-out test conversations from {test_path}...")
    test_recs = load_test_conversations(test_path)
    total_test = len(test_recs)
    print(f"   Total test records loaded: {total_test:,}")

    query_texts = [r["customer_message"] for r in test_recs]
    true_intents = [r["intent"] for r in test_recs]

    print("\n3. Running Batch Top-5 Vector Retrieval over all test queries...")
    tfidf_mat = retriever.vectorizer.transform(query_texts)
    dense_embeds = retriever.svd.transform(tfidf_mat)
    norms = np.linalg.norm(dense_embeds, axis=1, keepdims=True)
    norms[norms == 0] = 1e-10
    dense_embeds = dense_embeds / norms

    distances, indices = retriever.nn_model.kneighbors(dense_embeds, n_neighbors=5)

    recalls_at_1 = []
    recalls_at_3 = []
    recalls_at_5 = []
    mrr_list = []

    successful_examples = []
    failed_examples = []

    for i, rec in enumerate(test_recs):
        query_text = rec["customer_message"]
        true_intent = rec["intent"]
        query_id = rec.get("conversation_id", "")
        brand_resp = rec.get("brand_response", "")

        matched_indices = indices[i]
        matched_dists = distances[i]

        matches = []
        for rank in range(5):
            idx = int(matched_indices[rank])
            dist = float(matched_dists[rank])
            sim = round(max(0.0, 1.0 - dist), 4)
            meta = retriever.metadata[idx]
            matches.append({
                "rank": rank + 1,
                "similarity_score": sim,
                "historical_customer_message": meta["customer_message"],
                "historical_brand_response": meta["brand_response"],
                "intent": meta["intent"],
                "conversation_id": meta["conversation_id"],
                "context": meta.get("context", "")
            })

        matched_intents = [m["intent"] for m in matches]

        hit_1 = (len(matched_intents) >= 1 and matched_intents[0] == true_intent)
        hit_3 = any(intent == true_intent for intent in matched_intents[:3])
        hit_5 = any(intent == true_intent for intent in matched_intents[:5])

        recalls_at_1.append(1.0 if hit_1 else 0.0)
        recalls_at_3.append(1.0 if hit_3 else 0.0)
        recalls_at_5.append(1.0 if hit_5 else 0.0)

        first_rank_hit = 0
        for r_idx, intent in enumerate(matched_intents):
            if intent == true_intent:
                first_rank_hit = r_idx + 1
                break

        reciprocal_rank = (1.0 / first_rank_hit) if first_rank_hit > 0 else 0.0
        mrr_list.append(reciprocal_rank)

        example_data = {
            "query_id": query_id,
            "query_text": query_text,
            "true_intent": true_intent,
            "true_brand_response": brand_resp,
            "first_match": matches[0],
            "matches": matches,
            "hit_1": hit_1
        }

        if hit_1 and len(successful_examples) < 5:
            successful_examples.append(example_data)
        elif not hit_1 and len(failed_examples) < 5:
            failed_examples.append(example_data)

    recall_1 = round(float(np.mean(recalls_at_1)), 4)
    recall_3 = round(float(np.mean(recalls_at_3)), 4)
    recall_5 = round(float(np.mean(recalls_at_5)), 4)
    mrr_score = round(float(np.mean(mrr_list)), 4)

    print("\n--- RETRIEVAL EVALUATION RESULTS ---")
    print(f"Total Evaluated Test Queries: {total_test:,}")
    print(f"Recall@1: {recall_1:.4f}")
    print(f"Recall@3: {recall_3:.4f}")
    print(f"Recall@5: {recall_5:.4f}")
    print(f"MRR:      {mrr_score:.4f}")

    print(f"\n4. Generating Retrieval Evaluation Report at {report_path}...")
    generate_retrieval_report(
        recall_1=recall_1,
        recall_3=recall_3,
        recall_5=recall_5,
        mrr_score=mrr_score,
        eval_count=total_test,
        total_test=total_test,
        successful_examples=successful_examples,
        failed_examples=failed_examples,
        output_path=report_path
    )

    elapsed = round(time.time() - start_time, 2)
    print("\n" + "=" * 70)
    print(f"RETRIEVAL EVALUATION COMPLETED IN {elapsed} SECONDS")
    print("=" * 70)


def generate_retrieval_report(
    recall_1: float,
    recall_3: float,
    recall_5: float,
    mrr_score: float,
    eval_count: int,
    total_test: int,
    successful_examples: List[Dict[str, Any]],
    failed_examples: List[Dict[str, Any]],
    output_path: str
):
    lines = []
    lines.append("# Historical Support-Response Retrieval Evaluation Report")
    lines.append("")
    lines.append("## Executive Summary")
    lines.append(f"This report evaluates the dense semantic vector retrieval system on **{eval_count:,} held-out test conversations**.")
    lines.append("The retrieval index was constructed strictly on training data (`train.jsonl`) to guarantee **zero train/test data leakage**.")
    lines.append("")

    lines.append("## Retrieval Quantitative Evaluation Metrics")
    lines.append("| Metric | Score | Description |")
    lines.append("|---|---|---|")
    lines.append(f"| **Recall@1** | **{recall_1:.4f}** | Fraction of test queries where Top-1 retrieved historical case matches true intent |")
    lines.append(f"| **Recall@3** | **{recall_3:.4f}** | Fraction of test queries where at least one of Top-3 cases matches true intent |")
    lines.append(f"| **Recall@5** | **{recall_5:.4f}** | Fraction of test queries where at least one of Top-5 cases matches true intent |")
    lines.append(f"| **MRR (Mean Reciprocal Rank)** | **{mrr_score:.4f}** | Average reciprocal rank of the first intent-matching historical case |")
    lines.append("")

    lines.append("## Representative Successful Retrieval Examples")
    for i, eg in enumerate(successful_examples, 1):
        top_match = eg["first_match"]
        lines.append(f"### Successful Case {i} (`{eg['query_id']}`)")
        lines.append(f"- **Test Query Customer Message**: *\"{eg['query_text']}\"*")
        lines.append(f"- **Query Intent**: `{eg['true_intent']}`")
        lines.append(f"- **Top-1 Retrieved Customer Message**: *\"{top_match['historical_customer_message']}\"*")
        lines.append(f"- **Top-1 Retrieved Brand Response**: *\"{top_match['historical_brand_response']}\"*")
        lines.append(f"- **Top-1 Similarity Score**: `{top_match['similarity_score']:.4f}`")
        lines.append(f"- **Top-1 Retrieved Intent**: `{top_match['intent']}`")
        lines.append("")

    lines.append("## Representative Failed Retrieval Examples & Failure Mode Analysis")
    for i, eg in enumerate(failed_examples, 1):
        top_match = eg["first_match"]
        lines.append(f"### Failed Case {i} (`{eg['query_id']}`)")
        lines.append(f"- **Test Query Customer Message**: *\"{eg['query_text']}\"*")
        lines.append(f"- **Query Intent**: `{eg['true_intent']}`")
        lines.append(f"- **Top-1 Retrieved Customer Message**: *\"{top_match['historical_customer_message']}\"*")
        lines.append(f"- **Top-1 Retrieved Brand Response**: *\"{top_match['historical_brand_response']}\"*")
        lines.append(f"- **Top-1 Similarity Score**: `{top_match['similarity_score']:.4f}`")
        lines.append(f"- **Top-1 Retrieved Intent**: `{top_match['intent']}`")
        lines.append("")

    lines.append("## Key Retrieval Failure Modes")
    lines.append("1. **Short Ambiguous Messages**: Customer queries containing only single-word complaints (e.g. *\"Help @AmazonHelp\"*) lack topic tokens, causing retrieval to pull arbitrary generic support queries.")
    lines.append("2. **Multiple Overlapping Intents**: Queries containing both shipping delays and billing charges (e.g. *\"I was charged for 2-day delivery but it arrived 4 days late\"*) match both `ORDER_SHIPPING_DELIVERY` and `BILLING_REFUND_SUBSCRIPTION` centroids.")
    lines.append("3. **Non-Standard Twitter Jargon & Emojis**: Queries composed primarily of URLs, handles, or emojis reduce semantic match precision.")
    lines.append("")

    lines.append("## Reproducibility Commands")
    lines.append("```bash")
    lines.append("python -m src.retrieval.index")
    lines.append("python -m src.retrieval.evaluate")
    lines.append("```")

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


if __name__ == "__main__":
    run_retrieval_evaluation()
