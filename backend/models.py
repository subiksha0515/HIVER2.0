"""
Pydantic v2 request/response schemas for the AI Support Decision Engine API.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class ConversationTurn(BaseModel):
    author_id: str
    text: str
    inbound: bool = True


class SupportRequest(BaseModel):
    message: str = Field(..., min_length=1, description="Customer message to process")
    conversation_history: Optional[List[ConversationTurn]] = Field(
        default=[], description="Prior conversation turns"
    )


class RetrievedCase(BaseModel):
    conversation_id: str
    customer_message: str
    brand_response: str
    similarity_score: float
    intent: str
    rank: int


class SupportResponse(BaseModel):
    # Core decision fields
    decision: str  # "AUTO-HANDLE" or "ESCALATE"
    draft_reply: str
    escalation_reason: Optional[str] = None

    # Classification
    intent: str
    intent_confidence: float

    # Retrieval
    retrieved_cases: List[RetrievedCase]
    top_similarity: float

    # Evidence / grounding
    evidence: List[str]

    # Trust explanation
    trust_checks: List[Dict[str, Any]]

    # Internal stage
    pipeline_stage: str


class HealthResponse(BaseModel):
    status: str
    version: str


class StatusResponse(BaseModel):
    status: str
    classifier_loaded: bool
    retrieval_index_size: int
    model_name: str
    thresholds: Dict[str, float]
