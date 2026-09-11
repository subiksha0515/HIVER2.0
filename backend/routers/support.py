"""
Support query endpoint for the AI Support Decision Engine API.
"""

from typing import List, Dict, Any
from fastapi import APIRouter, Request, HTTPException
from backend.models import SupportRequest, SupportResponse, RetrievedCase

router = APIRouter()


def evaluate_trust_checks(
    customer_message: str,
    intent: str,
    confidence: float,
    retrieved_cases: List[Dict[str, Any]],
    top_similarity: float,
    escalation_engine: Any
) -> List[Dict[str, Any]]:
    """Generates detailed trust and safety check records for frontend transparency."""
    # Check 1: Supported Taxonomy
    pass_taxonomy = intent != "OTHER / UNKNOWN"
    c1 = {
        "check": "Supported Intent Taxonomy",
        "passed": pass_taxonomy,
        "detail": f"Intent '{intent}' is recognized." if pass_taxonomy else "Intent is unknown / outside taxonomy."
    }

    # Check 2: Intent Confidence
    min_conf = escalation_engine.min_intent_confidence
    pass_conf = confidence >= min_conf
    c2 = {
        "check": f"Intent Confidence (>= {int(min_conf * 100)}%)",
        "passed": pass_conf,
        "detail": f"Model confidence is {confidence * 100:.1f}% (threshold: {min_conf * 100:.0f}%)."
    }

    # Check 3: Retrieval Grounding Similarity
    min_sim = escalation_engine.min_retrieval_similarity
    pass_sim = top_similarity >= min_sim and len(retrieved_cases) > 0
    c3 = {
        "check": f"Historical Grounding (>= {int(min_sim * 100)}% sim)",
        "passed": pass_sim,
        "detail": f"Top similarity is {top_similarity * 100:.1f}% (threshold: {min_sim * 100:.0f}%)." if len(retrieved_cases) > 0 else "No historical cases retrieved."
    }

    # Check 4: Action Availability (Financial / Sensitive operations)
    has_action_conflict = False
    for rule in escalation_engine.compiled_action_rules:
        if rule.search(customer_message):
            has_action_conflict = True
            break
    c4 = {
        "check": "Permitted Action Scope",
        "passed": not has_action_conflict,
        "detail": "Permitted within autonomous response bounds." if not has_action_conflict else "Requires human-only action (financial refund, account deletion, or fraud/legal)."
    }

    # Check 5: Query Clarity
    is_ambiguous = False
    import re
    clean_msg = re.sub(r"https?://\S+", "", customer_message)
    clean_msg = re.sub(r"@\w+", "", clean_msg).strip()
    if len(clean_msg) < 5:
        is_ambiguous = True
    else:
        for rule in escalation_engine.compiled_ambiguity_rules:
            if rule.search(customer_message):
                is_ambiguous = True
                break
    c5 = {
        "check": "Query Clarity & Specificity",
        "passed": not is_ambiguous,
        "detail": "Query is sufficiently specific." if not is_ambiguous else "Query is ambiguous or lacks necessary context."
    }

    # Check 6: Consistent Guidance
    consistent_guidance = True
    if len(retrieved_cases) >= 3:
        retrieved_intents = [c.get("intent") for c in retrieved_cases[:3]]
        matching_count = sum(1 for i in retrieved_intents if i == intent)
        if matching_count == 0:
            consistent_guidance = False
    c6 = {
        "check": "Consistent Historical Guidance",
        "passed": consistent_guidance,
        "detail": "Historical evidence aligns with predicted intent." if consistent_guidance else "Historical evidence shows conflicting intents."
    }

    return [c1, c2, c3, c4, c5, c6]


@router.post("/api/support", response_model=SupportResponse, tags=["Support"])
async def process_support_query(request: Request, body: SupportRequest):
    """
    Process a customer support message through the end-to-end decision engine.
    Returns the intent, retrieved grounding cases, decision (AUTO-HANDLE / ESCALATE),
    draft reply, escalation reason if applicable, and trust safety checks.
    """
    message = body.message.strip()
    if not message:
        raise HTTPException(status_code=422, detail="Message cannot be empty.")

    pipeline = getattr(request.app.state, "pipeline", None)
    if pipeline is None:
        raise HTTPException(status_code=503, detail="Decision pipeline is not loaded.")

    # Convert conversation_history if provided
    history = []
    if body.conversation_history:
        for turn in body.conversation_history:
            history.append(turn.model_dump() if hasattr(turn, "model_dump") else dict(turn))

    try:
        pipeline_result = pipeline.process(
            customer_message=message,
            conversation_history=history,
            top_k=5
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Pipeline processing error: {str(exc)}")

    # Format retrieved cases
    raw_cases = pipeline_result.get("top_retrieved_cases", [])
    formatted_cases: List[RetrievedCase] = []
    for idx, case in enumerate(raw_cases):
        formatted_cases.append(
            RetrievedCase(
                conversation_id=str(case.get("conversation_id", f"case_{idx+1}")),
                customer_message=str(case.get("historical_customer_message") or case.get("customer_message", "")),
                brand_response=str(case.get("historical_brand_response") or case.get("brand_response", "")),
                similarity_score=float(round(case.get("similarity_score", 0.0), 4)),
                intent=str(case.get("intent", "UNKNOWN")),
                rank=int(case.get("rank", idx + 1))
            )
        )

    escalate = bool(pipeline_result.get("escalate", False))
    decision = "ESCALATE" if escalate else "AUTO-HANDLE"
    escalation_reason = pipeline_result.get("escalation_reason") if escalate else None
    top_similarity = float(round(pipeline_result.get("top_similarity", 0.0), 4))
    intent = str(pipeline_result.get("intent", "OTHER / UNKNOWN"))
    confidence = float(round(pipeline_result.get("confidence", 0.0), 4))
    draft_reply = str(pipeline_result.get("draft_reply", ""))
    evidence = [str(e) for e in pipeline_result.get("evidence", [])]
    pipeline_stage = str(pipeline_result.get("pipeline_stage", "COMPLETED"))

    trust_checks = evaluate_trust_checks(
        customer_message=message,
        intent=intent,
        confidence=confidence,
        retrieved_cases=raw_cases,
        top_similarity=top_similarity,
        escalation_engine=pipeline.escalation_engine
    )

    return SupportResponse(
        decision=decision,
        draft_reply=draft_reply,
        escalation_reason=escalation_reason,
        intent=intent,
        intent_confidence=confidence,
        retrieved_cases=formatted_cases,
        top_similarity=top_similarity,
        evidence=evidence,
        trust_checks=trust_checks,
        pipeline_stage=pipeline_stage
    )
