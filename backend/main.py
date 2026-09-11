"""
FastAPI application for AI Customer Support Decision Engine.
"""

import os
import sys
from contextlib import asynccontextmanager
from pathlib import Path

# Ensure root directory is in sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routers import health, support
from src.engine.pipeline import SupportDecisionPipeline


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager to load the AI pipeline models once at startup."""
    print("Starting AI Customer Support API...")
    classifier_path = os.getenv("CLASSIFIER_PATH", "models/best_intent_classifier.joblib")
    retrieval_index_dir = os.getenv("RETRIEVAL_INDEX_DIR", "models/retrieval_index")
    min_conf = float(os.getenv("MIN_INTENT_CONFIDENCE", "0.45"))
    min_sim = float(os.getenv("MIN_RETRIEVAL_SIMILARITY", "0.40"))

    app.state.pipeline = SupportDecisionPipeline(
        min_intent_confidence=min_conf,
        min_retrieval_similarity=min_sim,
        classifier_path=classifier_path,
        retrieval_index_dir=retrieval_index_dir
    )
    print("AI Customer Support API successfully initialized and ready.")
    yield
    print("Shutting down AI Customer Support API.")


app = FastAPI(
    title="AI Customer Support Decision Engine API",
    description="Grounded, deterministic escalation, and safe autonomous customer support assistant.",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS for local frontend development (Vite / Next.js)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(health.router)
app.include_router(support.router)


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("backend.main:app", host="0.0.0.0", port=port, reload=True)
