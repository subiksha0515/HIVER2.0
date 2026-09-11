"""
Health and status endpoints.
"""

from fastapi import APIRouter, Request
from backend.models import HealthResponse, StatusResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse, tags=["System"])
async def health():
    """Liveness probe — returns 200 if the application is running."""
    return HealthResponse(status="ok", version="1.0.0")


@router.get("/api/status", response_model=StatusResponse, tags=["System"])
async def status(request: Request):
    """Returns model load status and system configuration."""
    pipeline = request.app.state.pipeline
    classifier = pipeline.classifier
    retriever = pipeline.retriever

    # Retrieve index size safely
    try:
        if hasattr(retriever, "metadata") and retriever.metadata:
            index_size = len(retriever.metadata)
        elif hasattr(retriever, "embeddings") and retriever.embeddings is not None:
            index_size = len(retriever.embeddings)
        elif hasattr(retriever, "metadata_df"):
            index_size = int(retriever.metadata_df.shape[0])
        else:
            index_size = -1
    except Exception:
        index_size = -1

    return StatusResponse(
        status="ready",
        classifier_loaded=classifier is not None,
        retrieval_index_size=index_size,
        model_name="TF-IDF + LogisticRegression (Macro F1: 0.9199)",
        thresholds={
            "min_intent_confidence": pipeline.escalation_engine.min_intent_confidence,
            "min_retrieval_similarity": pipeline.escalation_engine.min_retrieval_similarity,
        }
    )
