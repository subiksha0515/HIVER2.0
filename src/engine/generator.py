"""
Grounded Response Generator.
Builds structured, grounded support responses backed by historical evidence.
LLM receives: customer_message, conversation_history, predicted_intent,
              intent_confidence, top_retrieved_cases, similarity_scores.
Generates structured JSON output with grounding evidence.
"""

import json
import re
from typing import Dict, Any, List

from src.engine.llm import BaseLLMClient


SYSTEM_PROMPT = """You are an AI customer support assistant for AmazonHelp.
Your job is to draft a professional, empathetic support reply for a customer query.

STRICT GROUNDING RULES — YOU MUST FOLLOW THESE WITHOUT EXCEPTION:
1. ONLY say things grounded in the historical support examples provided below.
2. NEVER invent policies, refund amounts, prices, shipping timelines, or account actions.
3. NEVER claim you have performed any action (e.g. "I have issued your refund").
4. NEVER make promises you cannot verify from the historical examples.
5. If the historical examples do not resolve the issue, say that the team will investigate further.
6. Keep the tone professional, empathetic, and concise (Twitter-style, under 280 characters if possible).
7. Your reply must begin with the customer handle if present.

Respond ONLY with a valid JSON object matching this schema exactly:
{
  "draft_reply": "<grounded response string>",
  "intent": "<detected intent label>",
  "confidence": <float>,
  "evidence": ["<supporting historical response 1>", "<supporting historical response 2>"],
  "escalate": false,
  "escalation_reason": ""
}
"""


def build_generation_prompt(
    customer_message: str,
    conversation_history: List[Dict],
    predicted_intent: str,
    intent_confidence: float,
    top_retrieved_cases: List[Dict[str, Any]]
) -> str:
    """Constructs the grounding prompt for the LLM."""

    # Format conversation context (last 4 turns max)
    context_lines = []
    for turn in conversation_history[-4:]:
        role = "Customer" if turn.get("inbound", True) else "AmazonHelp"
        context_lines.append(f"  [{role}]: {turn.get('text', '')}")
    context_str = "\n".join(context_lines) if context_lines else "  [No prior history]"

    # Format retrieved cases
    case_lines = []
    for i, case in enumerate(top_retrieved_cases[:5], 1):
        sim = case.get("similarity_score", 0.0)
        c_intent = case.get("intent", "UNKNOWN")
        hist_cust = case.get("historical_customer_message", "")
        hist_resp = case.get("historical_brand_response", "")
        case_lines.append(
            f"  Case {i} [Similarity: {sim:.4f}, Intent: {c_intent}]\n"
            f"    Customer: \"{hist_cust}\"\n"
            f"    Historical Response: \"{hist_resp}\""
        )
    cases_str = "\n".join(case_lines) if case_lines else "  [No retrieved historical cases]"

    prompt = f"""CUSTOMER SUPPORT CASE
=========================
Customer Message: "{customer_message}"

Predicted Intent: `{predicted_intent}`
Intent Confidence: {intent_confidence:.4f}

Conversation History (most recent):
{context_str}

TOP HISTORICAL SUPPORT CASES (Retrieved from AmazonHelp Twitter archive):
{cases_str}

TASK:
Using ONLY the historical support evidence above, draft a grounded reply.
Do NOT invent any facts, policies, promises, or account actions.
If the evidence is insufficient to answer, acknowledge and promise follow-up investigation.

Return ONLY valid JSON matching the schema in the system prompt.
"""
    return prompt


def generate_grounded_response(
    llm_client: BaseLLMClient,
    customer_message: str,
    conversation_history: List[Dict],
    predicted_intent: str,
    intent_confidence: float,
    top_retrieved_cases: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Calls LLM to generate a grounded response.
    Returns validated structured response dict.
    """
    prompt = build_generation_prompt(
        customer_message=customer_message,
        conversation_history=conversation_history,
        predicted_intent=predicted_intent,
        intent_confidence=intent_confidence,
        top_retrieved_cases=top_retrieved_cases
    )

    raw = llm_client.generate_json(prompt=prompt, system_prompt=SYSTEM_PROMPT)

    # Validate and normalise output schema
    result = {
        "draft_reply": str(raw.get("draft_reply", "")).strip(),
        "intent": str(raw.get("intent", predicted_intent)).strip(),
        "confidence": float(raw.get("confidence", intent_confidence)),
        "evidence": list(raw.get("evidence", [])),
        "escalate": bool(raw.get("escalate", False)),
        "escalation_reason": str(raw.get("escalation_reason", "")).strip()
    }
    return result
