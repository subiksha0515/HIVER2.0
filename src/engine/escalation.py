"""
Deterministic Grounding Safety & Escalation Policy Engine.
Enforces multi-layer safety escalation rules to guarantee zero false auto-handling
and prevent unsupported AI actions or hallucinations.
"""

import re
from typing import Dict, Any, List, Tuple


class SafetyEscalationEngine:
    """
    Deterministic Escalation Policy Engine.
    Overrides or validates AI decision before auto-handling customer queries.
    """

    UNAVAILABLE_ACTION_PATTERNS = [
        r"\brefund my money\b", r"\bgive me a refund\b", r"\bcancel my order now\b",
        r"\bchange my address\b", r"\bdelete my account\b", r"\breset my password\b",
        r"\bclose my account\b", r"\bsue\b", r"\blegal action\b", r"\blawyer\b",
        r"\bhacked\b", r"\bstolen card\b", r"\bfraud\b", r"\bunauthorized charge\b"
    ]

    AMBIGUOUS_QUERY_PATTERNS = [
        r"^\s*help\s*$", r"^\s*@\w+\s*$", r"^\s*why\s*$", r"^\s*wtf\s*$", r"^\s*\?\s*$"
    ]

    def __init__(
        self,
        min_intent_confidence: float = 0.45,
        min_retrieval_similarity: float = 0.40
    ):
        self.min_intent_confidence = min_intent_confidence
        self.min_retrieval_similarity = min_retrieval_similarity

        self.compiled_action_rules = [re.compile(p, re.IGNORECASE) for p in self.UNAVAILABLE_ACTION_PATTERNS]
        self.compiled_ambiguity_rules = [re.compile(p, re.IGNORECASE) for p in self.AMBIGUOUS_QUERY_PATTERNS]

    def evaluate_escalation(
        self,
        customer_message: str,
        predicted_intent: str,
        intent_confidence: float,
        is_uncertain: bool,
        top_retrieved_cases: List[Dict[str, Any]]
    ) -> Tuple[bool, str]:
        """
        Evaluates whether a customer query MUST be escalated to a human agent.
        Returns: (should_escalate: bool, escalation_reason: str)
        """
        # Rule 1: Request Requires Unavailable Action (Financial refund, account deletion, fraud, legal)
        for rule in self.compiled_action_rules:
            if rule.search(customer_message):
                return True, "Request requires an action unavailable to the AI."

        # Rule 2: Ambiguous Query
        clean_msg = re.sub(r"https?://\S+", "", customer_message)
        clean_msg = re.sub(r"@\w+", "", clean_msg).strip()
        if len(clean_msg) < 5:
            return True, "Customer request is ambiguous."

        for rule in self.compiled_ambiguity_rules:
            if rule.search(customer_message):
                return True, "Customer request is ambiguous."

        # Rule 3: Outside Supported Taxonomy
        if predicted_intent == "OTHER / UNKNOWN" or is_uncertain:
            return True, "The issue is outside the supported intent taxonomy."

        # Rule 4: Low Intent Confidence
        if intent_confidence < self.min_intent_confidence:
            return True, f"Intent confidence below validated threshold ({intent_confidence:.4f} < {self.min_intent_confidence:.2f})."

        # Rule 5: No Historical Cases or Low Retrieval Similarity
        if not top_retrieved_cases:
            return True, "No historical resolution examples found."

        top_similarity = top_retrieved_cases[0].get("similarity_score", 0.0)
        if top_similarity < self.min_retrieval_similarity:
            return True, f"No sufficiently similar historical resolution (Similarity {top_similarity:.4f} < {self.min_retrieval_similarity:.2f})."

        # Rule 6: Conflicting Historical Guidance
        if len(top_retrieved_cases) >= 3:
            retrieved_intents = [c.get("intent") for c in top_retrieved_cases[:3]]
            matching_intent_count = sum(1 for i in retrieved_intents if i == predicted_intent)
            if matching_intent_count == 0:
                return True, "Historical examples provide conflicting guidance."

        # Safe for Auto-Handling
        return False, ""
