"""
End-to-End AI Support Decision Engine Pipeline.
Orchestrates: Intent Classification -> Historical Case Retrieval ->
              Deterministic Escalation Check -> Grounded Response Generation.
"""

import json
import os
import time
import numpy as np
from pathlib import Path
from typing import Dict, Any, List, Optional

from src.intents.classifier import TFIDFClassifier
from src.retrieval.retrieve import ResponseRetriever
from src.engine.escalation import SafetyEscalationEngine
from src.engine.generator import generate_grounded_response
from src.engine.llm import get_llm_client


class SupportDecisionPipeline:
    """
    Full AI Customer Support Decision Engine.

    For a new customer message, executes:
    1. Intent Classification (TF-IDF + Logistic Regression)
    2. Historical Case Retrieval (Dense LSA vector search, Top-5)
    3. Deterministic Safety Escalation Check
    4. Grounded LLM Response Generation (if not escalated)
    5. Returns structured decision dict
    """

    def __init__(
        self,
        min_intent_confidence: float = 0.45,
        min_retrieval_similarity: float = 0.40,
        classifier_path: str = "models/best_intent_classifier.joblib",
        retrieval_index_dir: str = "models/retrieval_index"
    ):
        print("Initializing AI Support Decision Pipeline...")

        # 1. Load intent classifier
        import joblib
        print(f"  Loading intent classifier from {classifier_path}...")
        self.classifier = joblib.load(classifier_path)

        # 2. Load retrieval system
        print(f"  Loading retrieval system from {retrieval_index_dir}...")
        self.retriever = ResponseRetriever(retrieval_index_dir)

        # 3. Initialise escalation engine
        self.escalation_engine = SafetyEscalationEngine(
            min_intent_confidence=min_intent_confidence,
            min_retrieval_similarity=min_retrieval_similarity
        )

        # 4. Initialise LLM client
        self.llm_client = get_llm_client()

        print("Pipeline ready.")

    def process(
        self,
        customer_message: str,
        conversation_history: Optional[List[Dict]] = None,
        top_k: int = 5
    ) -> Dict[str, Any]:
        """
        Process a single customer message through the full pipeline.

        Returns:
        {
            "draft_reply": str,
            "intent": str,
            "confidence": float,
            "evidence": [str, ...],
            "escalate": bool,
            "escalation_reason": str,
            "top_retrieved_cases": [...],
            "top_similarity": float,
            "pipeline_stage": str
        }
        """
        if conversation_history is None:
            conversation_history = []

        # Step 1: Classify Intent
        intent_result = self.classifier.predict_one(customer_message)
        predicted_intent = intent_result["predicted_intent"]
        confidence = intent_result["confidence"]
        is_uncertain = intent_result["is_uncertain"]

        # Step 2: Retrieve Historical Cases
        top_retrieved_cases = self.retriever.retrieve(customer_message, top_k=top_k)
        top_similarity = top_retrieved_cases[0]["similarity_score"] if top_retrieved_cases else 0.0

        # Step 3: Deterministic Escalation Check
        should_escalate, escalation_reason = self.escalation_engine.evaluate_escalation(
            customer_message=customer_message,
            predicted_intent=predicted_intent,
            intent_confidence=confidence,
            is_uncertain=is_uncertain,
            top_retrieved_cases=top_retrieved_cases
        )

        if should_escalate:
            return {
                "draft_reply": "",
                "intent": predicted_intent,
                "confidence": confidence,
                "evidence": [],
                "escalate": True,
                "escalation_reason": escalation_reason,
                "top_retrieved_cases": top_retrieved_cases,
                "top_similarity": top_similarity,
                "pipeline_stage": "ESCALATED_PRE_GENERATION"
            }

        # Step 4: Grounded Response Generation
        response = generate_grounded_response(
            llm_client=self.llm_client,
            customer_message=customer_message,
            conversation_history=conversation_history,
            predicted_intent=predicted_intent,
            intent_confidence=confidence,
            top_retrieved_cases=top_retrieved_cases
        )

        # Step 5: Final safety override — if LLM tries to escalate, honour it
        if response.get("escalate", False):
            response["escalation_reason"] = response.get("escalation_reason") or "LLM determined escalation required."
            response["pipeline_stage"] = "ESCALATED_POST_GENERATION"
        else:
            response["pipeline_stage"] = "AUTO_HANDLED"

        response["top_retrieved_cases"] = top_retrieved_cases
        response["top_similarity"] = top_similarity
        return response


def load_pipeline_from_env(
    classifier_path: str = "models/best_intent_classifier.joblib",
    retrieval_index_dir: str = "models/retrieval_index"
) -> SupportDecisionPipeline:
    """Creates a SupportDecisionPipeline using thresholds from environment or validated defaults."""
    min_conf = float(os.getenv("MIN_INTENT_CONFIDENCE", "0.45"))
    min_sim = float(os.getenv("MIN_RETRIEVAL_SIMILARITY", "0.40"))
    return SupportDecisionPipeline(
        min_intent_confidence=min_conf,
        min_retrieval_similarity=min_sim,
        classifier_path=classifier_path,
        retrieval_index_dir=retrieval_index_dir
    )


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="AI Support Decision Pipeline")
    parser.add_argument("--tune-thresholds", action="store_true", help="Run validation threshold tuning")
    parser.add_argument("--query", type=str, default=None, help="Single query to test pipeline")
    args = parser.parse_args()

    if args.tune_thresholds:
        from src.engine.thresholds import tune_thresholds
        tune_thresholds()
    elif args.query:
        pipeline = load_pipeline_from_env()
        result = pipeline.process(args.query)
        print(json.dumps(result, indent=2))
    else:
        pipeline = load_pipeline_from_env()
        test_queries = [
            "Where is my package? Tracking hasn't updated in 3 days.",
            "I was charged twice for my Prime membership, I need a refund.",
            "My Kindle app keeps crashing on my iPhone.",
            "delete my account now",
            "help"
        ]
        print("\n" + "=" * 70)
        print("PIPELINE DEMO ON SAMPLE QUERIES")
        print("=" * 70)
        for q in test_queries:
            result = pipeline.process(q)
            print(f"\nQuery: \"{q}\"")
            print(f"  Intent: {result['intent']} (conf={result['confidence']:.4f})")
            print(f"  Top Similarity: {result['top_similarity']:.4f}")
            print(f"  Escalate: {result['escalate']}")
            if result["escalate"]:
                print(f"  Reason: {result['escalation_reason']}")
            else:
                print(f"  Draft Reply: {result['draft_reply'][:120]}...")
            print(f"  Stage: {result['pipeline_stage']}")
