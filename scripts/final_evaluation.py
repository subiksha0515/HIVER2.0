"""
Final Evaluation Runner.
Runs all evaluations in sequence from scratch without fabricating numbers:
1. Intent classification evaluation (test.jsonl)
2. Historical case retrieval evaluation (test.jsonl)
3. Escalation policy & coverage evaluation (5,000 samples)
4. Grounded response quality evaluation (500 samples)
Generates reports/final_evaluation.md with immutable empirical metrics.
"""

import os
import sys
import json
import time
from pathlib import Path
from typing import Dict, Any, List
import numpy as np

# Ensure root in sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import joblib
from sklearn.metrics import accuracy_score, precision_recall_fscore_support

from src.retrieval.retrieve import ResponseRetriever
from src.engine.escalation import SafetyEscalationEngine
from src.engine.pipeline import SupportDecisionPipeline
from src.evaluation.response_eval import evaluate_single_response


def evaluate_intent_classification(test_path: str = "data/processed/test.jsonl") -> Dict[str, Any]:
    print("\n[1/4] Running Intent Classification Evaluation...")
    classifier = joblib.load("models/best_intent_classifier.joblib")

    texts, y_true = [], []
    with open(test_path, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            r = json.loads(line)
            texts.append(r["customer_message"])
            y_true.append(r["intent"])

    preds = classifier.predict_batch(texts)
    y_pred = [p["predicted_intent"] for p in preds]

    acc = float(accuracy_score(y_true, y_pred))
    p_macro, r_macro, f1_macro, _ = precision_recall_fscore_support(y_true, y_pred, average="macro", zero_division=0)
    p_wt, r_wt, f1_wt, _ = precision_recall_fscore_support(y_true, y_pred, average="weighted", zero_division=0)

    results = {
        "total_test_samples": len(texts),
        "accuracy": round(acc, 4),
        "macro_precision": round(float(p_macro), 4),
        "macro_recall": round(float(r_macro), 4),
        "macro_f1": round(float(f1_macro), 4),
        "weighted_f1": round(float(f1_wt), 4),
    }
    print(f"   Accuracy: {results['accuracy']:.4f}, Macro F1: {results['macro_f1']:.4f}")
    return results


def evaluate_retrieval(test_path: str = "data/processed/test.jsonl", max_samples: int = 5000) -> Dict[str, Any]:
    print("\n[2/4] Running Retrieval Evaluation...")
    retriever = ResponseRetriever("models/retrieval_index")

    test_queries = []
    with open(test_path, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            r = json.loads(line)
            if r.get("customer_message"):
                test_queries.append(r)
            if len(test_queries) >= max_samples:
                break

    query_texts = [r["customer_message"] for r in test_queries]
    true_intents = [r["intent"] for r in test_queries]

    tfidf_mat = retriever.vectorizer.transform(query_texts)
    dense = retriever.svd.transform(tfidf_mat)
    norms = np.linalg.norm(dense, axis=1, keepdims=True)
    norms[norms == 0] = 1e-10
    dense = dense / norms
    distances, indices = retriever.nn_model.kneighbors(dense, n_neighbors=5)

    recall_at_1, recall_at_3, recall_at_5 = 0, 0, 0
    mrr_sum = 0.0

    for i in range(len(test_queries)):
        true_i = true_intents[i]
        top_k_metas = [retriever.metadata[idx] for idx in indices[i] if 0 <= idx < len(retriever.metadata)]
        retrieved_intents = [m["intent"] for m in top_k_metas]

        if len(retrieved_intents) > 0 and retrieved_intents[0] == true_i:
            recall_at_1 += 1
        if true_i in retrieved_intents[:3]:
            recall_at_3 += 1
        if true_i in retrieved_intents[:5]:
            recall_at_5 += 1

        mrr_val = 0.0
        for rank_pos, r_int in enumerate(retrieved_intents[:5], start=1):
            if r_int == true_i:
                mrr_val = 1.0 / rank_pos
                break
        mrr_sum += mrr_val

    n = len(test_queries)
    results = {
        "total_evaluated": n,
        "recall_at_1": round(recall_at_1 / n, 4),
        "recall_at_3": round(recall_at_3 / n, 4),
        "recall_at_5": round(recall_at_5 / n, 4),
        "mrr": round(mrr_sum / n, 4)
    }
    print(f"   Recall@1: {results['recall_at_1']:.4f}, Recall@3: {results['recall_at_3']:.4f}, Recall@5: {results['recall_at_5']:.4f}, MRR: {results['mrr']:.4f}")
    return results


def evaluate_escalation_and_coverage(test_path: str = "data/processed/test.jsonl", sample_size: int = 5000) -> Dict[str, Any]:
    print("\n[3/4] Running Escalation & Coverage Evaluation...")
    classifier = joblib.load("models/best_intent_classifier.joblib")
    retriever = ResponseRetriever("models/retrieval_index")
    engine = SafetyEscalationEngine(min_intent_confidence=0.45, min_retrieval_similarity=0.40)

    test_recs = []
    with open(test_path, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            r = json.loads(line)
            if r.get("customer_message"):
                test_recs.append(r)
            if len(test_recs) >= sample_size:
                break

    query_texts = [r["customer_message"] for r in test_recs]
    tfidf_mat = retriever.vectorizer.transform(query_texts)
    dense = retriever.svd.transform(tfidf_mat)
    norms = np.linalg.norm(dense, axis=1, keepdims=True)
    norms[norms == 0] = 1e-10
    dense = dense / norms
    distances, indices = retriever.nn_model.kneighbors(dense, n_neighbors=5)

    pred_results = classifier.predict_batch(query_texts)

    auto_handled = 0
    escalated = 0
    correct_intent_auto = 0
    reason_counts = {}

    for i, rec in enumerate(test_recs):
        msg = rec["customer_message"]
        true_intent = rec["intent"]
        pred = pred_results[i]

        top_sims = []
        for rank in range(5):
            idx = int(indices[i][rank])
            dist = float(distances[i][rank])
            top_sims.append({
                "rank": rank + 1,
                "similarity_score": round(max(0.0, 1.0 - dist), 4),
                "intent": retriever.metadata[idx]["intent"] if 0 <= idx < len(retriever.metadata) else "UNKNOWN"
            })

        should_esc, reason = engine.evaluate_escalation(
            customer_message=msg,
            predicted_intent=pred["predicted_intent"],
            intent_confidence=pred["confidence"],
            is_uncertain=pred["is_uncertain"],
            top_retrieved_cases=top_sims
        )

        if should_esc:
            escalated += 1
            cat_reason = reason
            if "Intent confidence below validated threshold" in reason:
                cat_reason = "Intent confidence below validated threshold (< 0.45)."
            elif "No sufficiently similar historical resolution" in reason:
                cat_reason = "No sufficiently similar historical resolution (< 0.40)."
            reason_counts[cat_reason] = reason_counts.get(cat_reason, 0) + 1
        else:
            auto_handled += 1
            if pred["predicted_intent"] == true_intent:
                correct_intent_auto += 1

    n = len(test_recs)
    coverage = auto_handled / n
    selective_acc = (correct_intent_auto / auto_handled) if auto_handled > 0 else 0.0

    results = {
        "total_evaluated": n,
        "auto_handled": auto_handled,
        "escalated": escalated,
        "coverage_rate": round(coverage, 4),
        "escalation_rate": round(escalated / n, 4),
        "selective_accuracy": round(selective_acc, 4),
        "reason_counts": reason_counts
    }
    print(f"   Coverage: {results['coverage_rate'] * 100:.2f}%, Selective Acc: {results['selective_accuracy'] * 100:.2f}%")
    return results


def evaluate_response_quality(test_path: str = "data/processed/test.jsonl", sample_size: int = 500) -> Dict[str, Any]:
    print("\n[4/4] Running Grounded Response Quality Evaluation...")
    pipeline = SupportDecisionPipeline(
        min_intent_confidence=0.45,
        min_retrieval_similarity=0.40,
        classifier_path="models/best_intent_classifier.joblib",
        retrieval_index_dir="models/retrieval_index"
    )

    test_recs = []
    with open(test_path, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            r = json.loads(line)
            if r.get("customer_message") and r.get("intent") != "OTHER / UNKNOWN":
                test_recs.append(r)
            if len(test_recs) >= sample_size:
                break

    all_scores = []
    unsupported_count = 0

    for i, rec in enumerate(test_recs):
        msg = rec["customer_message"]
        true_intent = rec["intent"]
        true_resp = rec.get("brand_response", "")
        conv_hist = rec.get("conversation_history", [])

        res = pipeline.process(msg, conversation_history=conv_hist, top_k=5)
        if not res.get("escalate", False):
            scores = evaluate_single_response(
                customer_message=msg,
                predicted_intent=res.get("intent", true_intent),
                draft_reply=res.get("draft_reply", ""),
                evidence=res.get("evidence", []),
                true_brand_response=true_resp
            )
            all_scores.append(scores)
            if scores["has_unsupported_claim"]:
                unsupported_count += 1

    total_evaluated = len(all_scores)
    avg_relevance = round(float(np.mean([s["relevance"] for s in all_scores])), 2) if total_evaluated else 0.0
    avg_groundedness = round(float(np.mean([s["groundedness"] for s in all_scores])), 2) if total_evaluated else 0.0
    avg_helpfulness = round(float(np.mean([s["helpfulness"] for s in all_scores])), 2) if total_evaluated else 0.0
    avg_tone = round(float(np.mean([s["tone"] for s in all_scores])), 2) if total_evaluated else 0.0
    unsupported_rate = round(unsupported_count / total_evaluated, 4) if total_evaluated else 0.0

    results = {
        "auto_handled_samples": total_evaluated,
        "avg_relevance": avg_relevance,
        "avg_groundedness": avg_groundedness,
        "avg_helpfulness": avg_helpfulness,
        "avg_tone": avg_tone,
        "unsupported_claim_rate": unsupported_rate
    }
    print(f"   Avg Groundedness: {avg_groundedness}/5, Unsupported Claim Rate: {unsupported_rate * 100:.2f}%")
    return results


def write_final_report(
    intent_res: Dict[str, Any],
    retrieval_res: Dict[str, Any],
    escalation_res: Dict[str, Any],
    response_res: Dict[str, Any],
    out_path: str = "reports/final_evaluation.md"
):
    print(f"\nWriting final evaluation report to {out_path}...")
    lines = [
        "# Final System Evaluation Report",
        "",
        "## Executive Summary",
        "This report provides the final, un-fabricated end-to-end evaluation of the AI Customer Support Decision Engine.",
        "All numbers are computed from scratch on the held-out test split (`data/processed/test.jsonl`).",
        "",
        "---",
        "",
        "## 1. Intent Classification Performance (Held-Out Test Set)",
        f"- **Evaluated Test Instances**: {intent_res['total_test_samples']:,}",
        f"- **Overall Accuracy**: **{intent_res['accuracy'] * 100:.2f}%**",
        f"- **Macro Precision**: **{intent_res['macro_precision']:.4f}**",
        f"- **Macro Recall**: **{intent_res['macro_recall']:.4f}**",
        f"- **Macro F1-Score**: **{intent_res['macro_f1']:.4f}**",
        f"- **Weighted F1-Score**: **{intent_res['weighted_f1']:.4f}**",
        "",
        "---",
        "",
        "## 2. Historical Case Retrieval Performance (Dense LSA Semantic Vector Search)",
        f"- **Evaluated Test Queries**: {retrieval_res['total_evaluated']:,}",
        f"- **Recall@1**: **{retrieval_res['recall_at_1'] * 100:.2f}%**",
        f"- **Recall@3**: **{retrieval_res['recall_at_3'] * 100:.2f}%**",
        f"- **Recall@5**: **{retrieval_res['recall_at_5'] * 100:.2f}%**",
        f"- **Mean Reciprocal Rank (MRR)**: **{retrieval_res['mrr']:.4f}**",
        "",
        "---",
        "",
        "## 3. Escalation Safety & Coverage Tradeoff (5,000 Sample Audit)",
        f"- **Total Audited**: {escalation_res['total_evaluated']:,}",
        f"- **Auto-Handled Rate**: **{escalation_res['coverage_rate'] * 100:.2f}%** ({escalation_res['auto_handled']:,} cases)",
        f"- **Escalated to Human Rate**: **{escalation_res['escalation_rate'] * 100:.2f}%** ({escalation_res['escalated']:,} cases)",
        f"- **Selective Accuracy on Auto-Handled**: **{escalation_res['selective_accuracy'] * 100:.2f}%**",
        "",
        "### Escalation Breakdown by Policy Rule",
        "| Policy Rule Trigger | Escalations Count | Share of Escalations |",
        "|---|---|---|"
    ]

    tot_esc = escalation_res["escalated"]
    for reason, count in sorted(escalation_res["reason_counts"].items(), key=lambda x: x[1], reverse=True):
        share = (count / tot_esc * 100) if tot_esc > 0 else 0.0
        lines.append(f"| `{reason}` | {count:,} | {share:.1f}% |")

    lines.extend([
        "",
        "---",
        "",
        "## 4. Response Generation Quality (Automated Grounding Rubrics)",
        f"- **Auto-Handled Responses Scored**: {response_res['auto_handled_samples']:,}",
        f"- **Average Relevance (1-5)**: **{response_res['avg_relevance']:.2f} / 5.0**",
        f"- **Average Groundedness (1-5)**: **{response_res['avg_groundedness']:.2f} / 5.0**",
        f"- **Average Helpfulness (1-5)**: **{response_res['avg_helpfulness']:.2f} / 5.0**",
        f"- **Average Tone (1-5)**: **{response_res['avg_tone']:.2f} / 5.0**",
        f"- **Unsupported Claim Rate (Hallucinations)**: **{response_res['unsupported_claim_rate'] * 100:.2f}%**",
        "",
        "---",
        "",
        "## 5. End-to-End Key System Metric Summary",
        "| Dimension | Metric | Measured Value | Standard / Target |",
        "|---|---|---|---|",
        f"| Intent Classification | Macro F1 | **{intent_res['macro_f1']:.4f}** | >= 0.85 |",
        f"| Case Retrieval | Recall@5 | **{retrieval_res['recall_at_5'] * 100:.2f}%** | >= 85.0% |",
        f"| Case Retrieval | MRR | **{retrieval_res['mrr']:.4f}** | >= 0.70 |",
        f"| Escalation Policy | Selective Accuracy | **{escalation_res['selective_accuracy'] * 100:.2f}%** | >= 95.0% |",
        f"| Generation Safety | Unsupported Claim Rate | **{response_res['unsupported_claim_rate'] * 100:.2f}%** | <= 5.0% |",
        f"| Generation Safety | Groundedness | **{response_res['avg_groundedness']:.2f} / 5.0** | >= 4.0 / 5.0 |",
        ""
    ])

    out_file = Path(out_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"Final report saved to {out_path}")


def main():
    start = time.time()
    print("=" * 75)
    print("AI CUSTOMER SUPPORT DECISION ENGINE — FINAL VERIFICATION EVALUATION")
    print("=" * 75)

    intent_res = evaluate_intent_classification()
    retrieval_res = evaluate_retrieval()
    escalation_res = evaluate_escalation_and_coverage()
    response_res = evaluate_response_quality()

    write_final_report(intent_res, retrieval_res, escalation_res, response_res)
    print(f"\nAll evaluations completed in {time.time() - start:.1f}s.")


if __name__ == "__main__":
    main()
