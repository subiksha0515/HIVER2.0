"""
Response Quality Evaluation Pipeline.
Evaluates generated support responses on a 1-5 rubric using automated scoring.
Measures: Correctness, Relevance, Groundedness, Helpfulness, Tone, Unsupported-Claim Rate.
NOTE: All evaluation in this module is AUTOMATED (algorithmic/heuristic), NOT human evaluation.
"""

import json
import re
import time
import numpy as np
from pathlib import Path
from typing import Dict, Any, List
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from src.engine.pipeline import load_pipeline_from_env


UNSUPPORTED_CLAIM_PATTERNS = [
    r"\bI have (issued|processed|refunded|cancelled|updated|sent|confirmed)\b",
    r"\byour refund (has been|will be) (issued|processed|sent|credited)\b",
    r"\bI (can|will) (give|send|issue|process|arrange)\b.*\brefund\b",
    r"\byour order (has been|will be) (cancelled|updated)\b",
    r"\bI have updated your (address|account|password)\b",
    r"\bguaranteed (delivery|refund|replacement)\b",
    r"\bwithin (24|48|72) hours? (you will|you'll) receive\b",
    r"\bI have escalated\b",
    r"\byou will receive (a refund|your (order|package)) by\b",
]

COMPILED_CLAIM_PATTERNS = [re.compile(p, re.IGNORECASE) for p in UNSUPPORTED_CLAIM_PATTERNS]


def score_groundedness(draft_reply: str, evidence: List[str]) -> int:
    """
    Automated groundedness score 1-5.
    Measures lexical overlap between draft_reply and historical evidence.
    """
    if not draft_reply.strip():
        return 1
    if not evidence:
        return 2

    vect = TfidfVectorizer(ngram_range=(1, 2), min_df=1)
    try:
        all_texts = [draft_reply] + [e for e in evidence if e.strip()]
        tfidf = vect.fit_transform(all_texts)
        sims = cosine_similarity(tfidf[0:1], tfidf[1:]).flatten()
        max_sim = float(np.max(sims)) if len(sims) > 0 else 0.0
    except Exception:
        max_sim = 0.0

    if max_sim >= 0.5:
        return 5
    elif max_sim >= 0.35:
        return 4
    elif max_sim >= 0.20:
        return 3
    elif max_sim >= 0.08:
        return 2
    else:
        return 1


def score_relevance(draft_reply: str, customer_message: str, predicted_intent: str) -> int:
    """
    Automated relevance score 1-5.
    Measures lexical similarity between reply and customer message + intent keywords.
    """
    if not draft_reply.strip():
        return 1

    intent_key_map = {
        "ORDER_SHIPPING_DELIVERY": ["order", "package", "delivery", "shipping", "tracking"],
        "BILLING_REFUND_SUBSCRIPTION": ["charge", "refund", "payment", "bill", "subscription"],
        "ACCOUNT_LOGIN_SECURITY": ["account", "login", "password", "locked", "access"],
        "APP_CRASH_PERFORMANCE": ["app", "crash", "slow", "freeze", "performance"],
        "BATTERY_POWER_CHARGING": ["battery", "charge", "charger", "power"],
        "SOFTWARE_UPDATE_ISSUES": ["update", "software", "version", "upgrade"],
        "CONNECTIVITY_NETWORK_WIFI": ["wifi", "network", "connection", "bluetooth"],
        "AUDIO_SPEAKER_MICROPHONE": ["sound", "speaker", "audio", "volume", "mic"],
        "DISPLAY_SCREEN_PHYSICAL": ["screen", "display", "cracked", "flicker"],
        "STORE_REPAIR_SERVICE": ["repair", "warranty", "store", "replace", "service"],
    }

    intent_keywords = intent_key_map.get(predicted_intent, [])
    reply_lower = draft_reply.lower()

    keyword_hits = sum(1 for kw in intent_keywords if kw in reply_lower)
    keyword_score = min(keyword_hits / max(len(intent_keywords), 1), 1.0)

    try:
        vect = TfidfVectorizer(ngram_range=(1, 2), min_df=1)
        tfidf = vect.fit_transform([draft_reply, customer_message])
        sim = float(cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0])
    except Exception:
        sim = 0.0

    combined = 0.5 * keyword_score + 0.5 * sim
    if combined >= 0.4:
        return 5
    elif combined >= 0.28:
        return 4
    elif combined >= 0.16:
        return 3
    elif combined >= 0.06:
        return 2
    else:
        return 1


def score_tone(draft_reply: str) -> int:
    """
    Automated tone score 1-5.
    Checks for professional support markers and absence of aggressive language.
    """
    if not draft_reply.strip():
        return 1

    reply_lower = draft_reply.lower()
    positive_markers = ["sorry", "apolog", "understand", "help", "look into", "assist",
                        "thank", "please", "happy", "team", "investigate", "support"]
    aggressive_markers = ["stupid", "idiot", "shut up", "not my problem", "impossible"]

    pos_hits = sum(1 for m in positive_markers if m in reply_lower)
    agg_hits = sum(1 for m in aggressive_markers if m in reply_lower)

    if agg_hits > 0:
        return 1
    if pos_hits >= 3:
        return 5
    elif pos_hits >= 2:
        return 4
    elif pos_hits >= 1:
        return 3
    elif len(draft_reply.split()) >= 10:
        return 2
    else:
        return 1


def detect_unsupported_claims(draft_reply: str) -> List[str]:
    """Detects unsupported factual claims in a draft reply."""
    found = []
    for pattern in COMPILED_CLAIM_PATTERNS:
        m = pattern.search(draft_reply)
        if m:
            found.append(m.group(0))
    return found


def evaluate_single_response(
    customer_message: str,
    predicted_intent: str,
    draft_reply: str,
    evidence: List[str],
    true_brand_response: str = ""
) -> Dict[str, Any]:
    """Evaluates a single draft response on all 1-5 rubrics."""
    if not draft_reply.strip():
        return {
            "groundedness": 1,
            "relevance": 1,
            "tone": 1,
            "correctness": 1,
            "helpfulness": 1,
            "overall": 1.0,
            "unsupported_claims": [],
            "has_unsupported_claim": False
        }

    g = score_groundedness(draft_reply, evidence)
    r = score_relevance(draft_reply, customer_message, predicted_intent)
    t = score_tone(draft_reply)
    unsupported = detect_unsupported_claims(draft_reply)

    # Correctness proxy: similarity to true brand response if available
    correctness = 3  # default
    if true_brand_response:
        try:
            vect = TfidfVectorizer(ngram_range=(1, 2), min_df=1)
            tfidf = vect.fit_transform([draft_reply, true_brand_response])
            sim = float(cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0])
            correctness = min(5, max(1, int(sim * 10) + 1))
        except Exception:
            correctness = 3

    helpfulness = max(1, min(5, (g + r + t) // 3))
    overall = round(np.mean([g, r, t, correctness, helpfulness]), 2)

    return {
        "groundedness": g,
        "relevance": r,
        "tone": t,
        "correctness": correctness,
        "helpfulness": helpfulness,
        "overall": overall,
        "unsupported_claims": unsupported,
        "has_unsupported_claim": len(unsupported) > 0
    }


def run_response_evaluation(
    test_path: str = "data/processed/test.jsonl",
    eval_sample: int = 500,
    report_path: str = "reports/response_evaluation.md"
):
    start = time.time()
    print("=" * 70)
    print("RESPONSE QUALITY EVALUATION PIPELINE")
    print("NOTE: All evaluation is AUTOMATED (algorithmic/heuristic).")
    print("      This is NOT human evaluation.")
    print("=" * 70)

    pipeline = load_pipeline_from_env()

    print(f"\nLoading {eval_sample} test samples from {test_path}...")
    test_recs = []
    with open(test_path, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            r = json.loads(line)
            if r.get("customer_message") and r.get("intent") != "OTHER / UNKNOWN":
                test_recs.append(r)
            if len(test_recs) >= eval_sample:
                break

    print(f"Running pipeline on {len(test_recs):,} test samples...")

    all_scores = []
    all_escalated = []
    unsupported_count = 0
    intent_scores = {}

    for i, rec in enumerate(test_recs):
        msg = rec["customer_message"]
        true_intent = rec["intent"]
        true_resp = rec.get("brand_response", "")
        conv_hist = rec.get("conversation_history", [])

        result = pipeline.process(msg, conversation_history=conv_hist, top_k=5)
        escalated = result.get("escalate", False)
        all_escalated.append(escalated)

        if not escalated:
            scores = evaluate_single_response(
                customer_message=msg,
                predicted_intent=result.get("intent", true_intent),
                draft_reply=result.get("draft_reply", ""),
                evidence=result.get("evidence", []),
                true_brand_response=true_resp
            )
            all_scores.append(scores)
            if scores["has_unsupported_claim"]:
                unsupported_count += 1

            if true_intent not in intent_scores:
                intent_scores[true_intent] = []
            intent_scores[true_intent].append(scores["overall"])

        if (i + 1) % 100 == 0:
            print(f"  Processed {i + 1}/{len(test_recs)} samples...")

    auto_count = sum(1 for e in all_escalated if not e)
    esc_count = sum(1 for e in all_escalated if e)
    total = len(all_escalated)

    avg_scores = {}
    if all_scores:
        for key in ["groundedness", "relevance", "tone", "correctness", "helpfulness", "overall"]:
            avg_scores[key] = round(float(np.mean([s[key] for s in all_scores])), 3)

    unsupported_rate = round(unsupported_count / max(auto_count, 1), 4)

    print(f"\nResults on {total} test samples:")
    print(f"  Auto-handled: {auto_count} ({auto_count/total:.1%})")
    print(f"  Escalated:    {esc_count} ({esc_count/total:.1%})")
    print(f"  Unsupported-Claim Rate: {unsupported_rate:.4f}")
    if avg_scores:
        for k, v in avg_scores.items():
            print(f"  Avg {k}: {v:.3f} / 5.0")

    _write_response_eval_report(
        avg_scores=avg_scores,
        unsupported_rate=unsupported_rate,
        auto_count=auto_count,
        esc_count=esc_count,
        total=total,
        intent_scores=intent_scores,
        all_scores=all_scores,
        output_path=report_path
    )

    elapsed = round(time.time() - start, 2)
    print(f"\nReport saved to {report_path}. Done in {elapsed}s.")
    return avg_scores, unsupported_rate, auto_count / total


def _write_response_eval_report(
    avg_scores, unsupported_rate, auto_count, esc_count, total, intent_scores, all_scores, output_path
):
    lines = []
    lines.append("# Response Quality Evaluation Report")
    lines.append("")
    lines.append("> [!NOTE]")
    lines.append("> All evaluation in this report is **AUTOMATED** using algorithmic/heuristic scoring.")
    lines.append("> This is **NOT human evaluation**. Scores are approximate and should be")
    lines.append("> supplemented with manual review before production deployment.")
    lines.append("")
    lines.append("## Overview")
    lines.append(f"- **Total test samples evaluated**: {total:,}")
    lines.append(f"- **Auto-handled**: {auto_count:,} ({auto_count/total:.1%})")
    lines.append(f"- **Escalated**: {esc_count:,} ({esc_count/total:.1%})")
    lines.append(f"- **Unsupported-Claim Rate** (auto-handled only): {unsupported_rate:.4f} ({unsupported_rate*100:.2f}%)")
    lines.append("")

    lines.append("## Automated Quality Rubric Scores (1-5 Scale, Auto-Handled Responses Only)")
    lines.append("| Dimension | Average Score (1-5) | Description |")
    lines.append("|---|---|---|")
    rubric_desc = {
        "groundedness": "Lexical overlap between reply and historical evidence",
        "relevance": "Keyword & semantic match to customer message + intent",
        "tone": "Professional, empathetic tone markers",
        "correctness": "Similarity to true historical brand response",
        "helpfulness": "Composite of groundedness, relevance, tone",
        "overall": "Mean across all rubric dimensions"
    }
    for k, v in avg_scores.items():
        stars = "⭐" * max(1, round(v))
        lines.append(f"| **{k.capitalize()}** | **{v:.3f}** {stars} | {rubric_desc.get(k, '')} |")
    lines.append("")

    lines.append("## Per-Intent Average Overall Score")
    lines.append("| Intent | Avg Score | Sample Count |")
    lines.append("|---|---|---|")
    for intent, scores in sorted(intent_scores.items()):
        avg = round(float(np.mean(scores)), 3)
        lines.append(f"| `{intent}` | {avg:.3f} | {len(scores)} |")
    lines.append("")

    lines.append("## Evaluation Rubric Definition")
    lines.append("| Score | Meaning |")
    lines.append("|---|---|")
    lines.append("| **5** | Excellent — Fully grounded, relevant, professional, matches historical patterns |")
    lines.append("| **4** | Good — Mostly grounded and relevant with minor gaps |")
    lines.append("| **3** | Acceptable — Partially grounded; some gaps in relevance or tone |")
    lines.append("| **2** | Poor — Weak grounding or low relevance; needs human review |")
    lines.append("| **1** | Failing — Not grounded, irrelevant, or empty |")
    lines.append("")

    lines.append("## Reproducibility")
    lines.append("```bash")
    lines.append("python -m src.evaluation.response_eval")
    lines.append("```")

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


if __name__ == "__main__":
    run_response_evaluation()
