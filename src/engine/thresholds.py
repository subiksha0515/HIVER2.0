"""
Validation-Set Threshold Tuning for Safety Escalation Engine.
Sweeps intent confidence and retrieval similarity thresholds over val.jsonl
to find the safety-prioritized operating point that minimizes False Auto-Handling.
"""

import json
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Any


def load_val_data(val_path: str = "data/processed/val.jsonl") -> List[Dict[str, Any]]:
    records = []
    with open(val_path, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            r = json.loads(line)
            if r.get("customer_message"):
                records.append(r)
    return records


def simulate_escalation(
    intent: str,
    confidence: float,
    is_uncertain: bool,
    top_similarity: float,
    min_intent_conf: float,
    min_similarity: float
) -> bool:
    """Lightweight deterministic escalation check for threshold sweeping."""
    if intent == "OTHER / UNKNOWN" or is_uncertain:
        return True
    if confidence < min_intent_conf:
        return True
    if top_similarity < min_similarity:
        return True
    return False


def sweep_thresholds(
    val_records: List[Dict[str, Any]],
    retrieval_results: Dict[str, List[Dict]],
    conf_range: np.ndarray,
    sim_range: np.ndarray
) -> Dict[str, Any]:
    """
    Sweeps thresholds over validation set and computes key safety metrics.
    Priority: Minimize False Auto-Handling (dangerous), secondary: maximise automation.

    A record is considered "needs human" if:
       - its intent is OTHER / UNKNOWN  (can't be grounded)
       - OR it would require an action we cannot perform

    Since we don't have ground-truth labels for "requires human",
    we approximate: needs_human = (true_intent == "OTHER / UNKNOWN")
    """
    results_grid = {}

    for min_conf in conf_range:
        for min_sim in sim_range:
            n_auto = 0
            n_escalate = 0
            n_needs_human = 0
            n_false_auto = 0       # auto-handled but should have escalated
            n_false_escalate = 0   # escalated but could have been auto-handled

            for rec in val_records:
                true_intent = rec.get("intent", "OTHER / UNKNOWN")
                confidence = rec.get("intent_confidence", 0.5)
                is_uncertain = (confidence < 0.3) or (true_intent == "OTHER / UNKNOWN")

                top_sim = 0.0
                conv_id = rec.get("conversation_id", "")
                if conv_id in retrieval_results and retrieval_results[conv_id]:
                    top_sim = retrieval_results[conv_id][0].get("similarity_score", 0.0)

                escalated = simulate_escalation(
                    intent=true_intent,
                    confidence=confidence,
                    is_uncertain=is_uncertain,
                    top_similarity=top_sim,
                    min_intent_conf=float(min_conf),
                    min_similarity=float(min_sim)
                )

                # Ground truth proxy: unknown intents or low-confidence should be human
                needs_human = (true_intent == "OTHER / UNKNOWN") or (confidence < 0.3)

                if needs_human:
                    n_needs_human += 1

                if escalated:
                    n_escalate += 1
                    if not needs_human:
                        n_false_escalate += 1
                else:
                    n_auto += 1
                    if needs_human:
                        n_false_auto += 1

            n_total = len(val_records)
            auto_rate = n_auto / n_total
            esc_rate = n_escalate / n_total
            false_auto_rate = n_false_auto / n_total
            false_esc_rate = n_false_escalate / n_total

            results_grid[(round(float(min_conf), 2), round(float(min_sim), 2))] = {
                "auto_rate": round(auto_rate, 4),
                "escalation_rate": round(esc_rate, 4),
                "false_auto_rate": round(false_auto_rate, 4),
                "false_escalation_rate": round(false_esc_rate, 4),
                "n_false_auto": n_false_auto,
                "n_false_escalate": n_false_escalate
            }

    return results_grid


def find_safe_thresholds(results_grid: Dict) -> Tuple[float, float, Dict]:
    """
    Selects the threshold pair that achieves:
    1. Zero false auto-handling (STRICT requirement)
    2. Minimum escalation rate among safe options
    """
    safe_candidates = {
        k: v for k, v in results_grid.items()
        if v["false_auto_rate"] == 0.0
    }

    if not safe_candidates:
        # Relax to min false auto rate
        min_far = min(v["false_auto_rate"] for v in results_grid.values())
        safe_candidates = {k: v for k, v in results_grid.items()
                           if v["false_auto_rate"] == min_far}

    best_key = min(safe_candidates, key=lambda k: safe_candidates[k]["escalation_rate"])
    best_metrics = safe_candidates[best_key]
    best_conf_thresh, best_sim_thresh = best_key
    return best_conf_thresh, best_sim_thresh, best_metrics


def tune_thresholds(
    val_path: str = "data/processed/val.jsonl",
    retrieval_index_dir: str = "models/retrieval_index"
) -> Tuple[float, float, Dict]:
    """Main threshold tuning entry point. Returns (best_conf_thresh, best_sim_thresh, metrics)."""
    print("=" * 70)
    print("THRESHOLD TUNING ON VALIDATION SET")
    print("=" * 70)

    val_records = load_val_data(val_path)
    print(f"Loaded {len(val_records):,} validation records.")

    # Perform batch retrieval for all val records to get similarity scores
    print("Running batch retrieval for val records...")
    from src.retrieval.retrieve import ResponseRetriever
    retriever = ResponseRetriever(retrieval_index_dir)

    query_texts = [r["customer_message"] for r in val_records]
    conv_ids = [r.get("conversation_id", str(i)) for i, r in enumerate(val_records)]

    # Batch transform
    tfidf_mat = retriever.vectorizer.transform(query_texts)
    dense_embeds = retriever.svd.transform(tfidf_mat)
    norms = np.linalg.norm(dense_embeds, axis=1, keepdims=True)
    norms[norms == 0] = 1e-10
    dense_embeds = dense_embeds / norms

    distances, indices = retriever.nn_model.kneighbors(dense_embeds, n_neighbors=1)

    retrieval_results = {}
    for i, cid in enumerate(conv_ids):
        idx = int(indices[i][0])
        sim = round(max(0.0, 1.0 - float(distances[i][0])), 4)
        meta = retriever.metadata[idx]
        retrieval_results[cid] = [{"similarity_score": sim, "intent": meta["intent"]}]

    # Sweep thresholds
    conf_range = np.arange(0.30, 0.75, 0.05)
    sim_range = np.arange(0.20, 0.65, 0.05)
    print(f"Sweeping {len(conf_range) * len(sim_range)} threshold combinations...")
    results_grid = sweep_thresholds(val_records, retrieval_results, conf_range, sim_range)

    best_conf, best_sim, best_metrics = find_safe_thresholds(results_grid)

    print(f"\nBest Validated Thresholds:")
    print(f"  Min Intent Confidence : {best_conf:.2f}")
    print(f"  Min Retrieval Similarity : {best_sim:.2f}")
    print(f"  Auto-Handling Rate     : {best_metrics['auto_rate']:.4f}")
    print(f"  Escalation Rate        : {best_metrics['escalation_rate']:.4f}")
    print(f"  False Auto-Handle Rate : {best_metrics['false_auto_rate']:.4f}")
    print(f"  False Escalation Rate  : {best_metrics['false_escalation_rate']:.4f}")

    return best_conf, best_sim, best_metrics


if __name__ == "__main__":
    tune_thresholds()
