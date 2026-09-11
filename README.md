# AI Customer Support Decision Engine

An enterprise-grade, grounded customer support decision engine with deterministic safety escalation, dense semantic vector retrieval, and transparent decision-making.

---

## 1. System Architecture Overview

```
Customer Message
       │
       ▼
┌─────────────────────────────────────────────────────────────┐
│ 1. Intent Classifier (TF-IDF + Logistic Regression)         │
│    - Predicts Intent + Calibrated Confidence Score          │
└──────────────────────────────┬──────────────────────────────┘
                               │
       ┌───────────────────────┴───────────────────────┐
       ▼                                               ▼
┌────────────────────────────────────────┐ ┌──────────────────────────────────────┐
│ 2. Historical Case Retriever           │ │ 3. Deterministic Safety Escalation   │
│    - 57,036 train conversations        │ │    - Rule 1: Prohibited Actions      │
│    - TF-IDF + SVD (128d) + Cosine NN   │ │    - Rule 2: Ambiguous/Short Query   │
│    - Top-5 nearest resolved cases      │ │    - Rule 3: Outside Taxonomy        │
└──────────────────┬─────────────────────┘ │    - Rule 4: Intent Conf < 0.45      │
                   │                       │    - Rule 5: Similarity < 0.40       │
                   │                       │    - Rule 6: Historical Conflict     │
                   ▼                       └──────────────────┬───────────────────┘
       ┌──────────────────────────────────────────────────────┘
       │
       ├─── Should Escalate? (True) ───► [ESCALATE TO HUMAN AGENT]
       │                                 (Includes exact policy violation reason)
       │
       └─── Safe? (False) ─────────────► [GROUNDED RESPONSE GENERATION]
                                         - Synthesizes reply strictly from
                                           top retrieved resolutions.
                                         - Hallucination & claim validator.
                                         - [AUTO-HANDLE DECISION]
```

---

## 2. Dataset & Leakage-Free Splitting

The dataset is derived from Twitter Customer Support interactions for Amazon (`@AmazonHelp`).
All conversations are reconstructed end-to-end and split strictly by **`conversation_id`**:

| Split | Count | Share | Overlap with Test | Overlap with Val |
|---|---|---|---|---|
| `train.jsonl` | **57,036** | 70% | **0** | **0** |
| `val.jsonl` | **12,222** | 15% | **0** | — |
| `test.jsonl` | **12,222** | 15% | — | **0** |
| `temporal_test.jsonl`| **12,222** | 15% (latest 15% by timestamp) | 0 | 0 |

- **Retrieval Index Provenance**: Built strictly on `train.jsonl` (57,036 entries). Zero contamination from test or validation sets.
- Full audit available in `reports/leakage_audit.md`.

---

## 3. Intent Classification Performance

Evaluated on **12,222 held-out test instances**:

| Classifier | Test Accuracy | Macro Precision | Macro Recall | Macro F1 |
|---|---|---|---|---|
| Majority Class Baseline | 48.30% | 0.0439 | 0.0909 | 0.0592 |
| Rule / Keyword Baseline | 80.67% | 0.7398 | 0.5593 | 0.5803 |
| Embedding KNN Baseline | 63.96% | 0.5417 | 0.4425 | 0.4367 |
| **TF-IDF + Logistic Regression (Selected)** | **96.81%** | **0.9325** | **0.9120** | **0.9199** |

---

## 4. Historical Case Retrieval

- **Index Algorithm**: TF-IDF Vectorizer + TruncatedSVD (128 latent semantic dimensions) + Cosine Nearest Neighbors.
- **Recall@1**: **64.84%**
- **Recall@3**: **85.58%**
- **Recall@5**: **90.02%**
- **Mean Reciprocal Rank (MRR)**: **0.7460**

---

## 5. Grounded Safety Escalation Policy

To guarantee zero unauthorized actions and zero hallucinations, all queries undergo a 6-layer deterministic safety check:

1. **Unavailable Actions**: Financial transactions, account deletions, password resets, fraud, lawsuits are immediately blocked.
2. **Ambiguous Queries**: Single words (`help`, `?`, `@AmazonHelp`) are escalated for human clarification.
3. **Out of Taxonomy**: Unrecognized problems (`OTHER / UNKNOWN` or low confidence) escalate.
4. **Intent Confidence Threshold**: Required $\ge 0.45$.
5. **Retrieval Grounding Similarity**: Required $\ge 0.40$ cosine similarity.
6. **Consistent Historical Guidance**: At least 1 matching intent among top-3 retrieved historical resolutions.

---

## 6. End-to-End System Evaluation (Empirical Results)

Audit on 5,000 held-out test queries (`reports/final_evaluation.md`):

| Metric | Measured Value | Standard Target | Status |
|---|---|---|---|
| Intent Macro F1 | **0.9199** | $\ge 0.85$ | Passed |
| Retrieval Recall@5 | **90.02%** | $\ge 85.0\%$ | Passed |
| Retrieval MRR | **0.7460** | $\ge 0.70$ | Passed |
| Escalation Coverage | **39.30%** (1,965 auto-handled) | Calibrated | Passed |
| Human Escalation Rate | **60.70%** (3,035 escalated) | Safety-first | Passed |
| Selective Accuracy | **96.95%** | $\ge 95.0\%$ | Passed |
| Unsupported Claim Rate | **0.00%** | $\le 5.0\%$ | Passed |
| Response Groundedness | **5.00 / 5.0** | $\ge 4.0$ | Passed |

---

## 7. FastAPI Backend API

### Endpoints

- **`GET /health`**: Health liveness check.
- **`GET /api/status`**: Pipeline status, classifier health, index size, and active thresholds.
- **`POST /api/support`**: Process a customer message and return decision, intent, evidence, and trust checks.

#### Example Request:
```bash
curl -X POST "http://localhost:8000/api/support" \
  -H "Content-Type: application/json" \
  -d '{"message": "Where is my package? The tracking number has not updated in 3 days."}'
```

#### Example Response:
```json
{
  "decision": "AUTO-HANDLE",
  "draft_reply": "I'm sorry for the delay with your delivery! Please check the latest tracking status...",
  "escalation_reason": null,
  "intent": "ORDER_SHIPPING_DELIVERY",
  "intent_confidence": 0.9425,
  "retrieved_cases": [
    {
      "conversation_id": "conv_12345",
      "customer_message": "My parcel tracking is stuck",
      "brand_response": "We apologize! You can check your delivery details here...",
      "similarity_score": 0.642,
      "intent": "ORDER_SHIPPING_DELIVERY",
      "rank": 1
    }
  ],
  "top_similarity": 0.642,
  "evidence": ["..."],
  "trust_checks": [
    {"check": "Supported Intent Taxonomy", "passed": true, "detail": "Intent 'ORDER_SHIPPING_DELIVERY' is recognized."},
    {"check": "Intent Confidence (>= 45%)", "passed": true, "detail": "Model confidence is 94.2% (threshold: 45%)."},
    {"check": "Historical Grounding (>= 40% sim)", "passed": true, "detail": "Top similarity is 64.2% (threshold: 40%)."},
    {"check": "Permitted Action Scope", "passed": true, "detail": "Permitted within autonomous response bounds."},
    {"check": "Query Clarity & Specificity", "passed": true, "detail": "Query is sufficiently specific."},
    {"check": "Consistent Historical Guidance", "passed": true, "detail": "Historical evidence aligns with predicted intent."}
  ],
  "pipeline_stage": "AUTO_HANDLED"
}
```

---

## 8. Test Suite

16 automated unit and end-to-end integration tests:
```bash
python -m pytest tests/ -v
```
- `tests/test_e2e.py`: 8 end-to-end pipeline categories verifying zero false auto-handling on prohibited actions, ambiguous queries, and confidence thresholds.
- `tests/test_api.py`: 8 FastAPI HTTP endpoint tests covering health, status, validation, and auto-handling logic.

---

## 9. Running the Application

### 1. Start the Backend API
```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```
Interactive Swagger documentation is available at `http://localhost:8000/docs`.

### 2. Start the Frontend Application
```bash
cd frontend
npm install
npm run dev
```
Open `http://localhost:5173` to interact with the Decision Engine UI.

---

## 10. Reproducibility & Evaluation Scripts

```bash
# Run full empirical evaluation suite
python scripts/final_evaluation.py

# Run standalone component evaluations
python -m src.intents.evaluate
python -m src.retrieval.evaluate
python -m src.evaluation.escalation_eval
python -m src.evaluation.response_eval
python -m src.evaluation.ablation
```

---

## 11. Reports Reference

- `reports/final_evaluation.md`: Full end-to-end evaluation metrics.
- `reports/leakage_audit.md`: Data leakage and split audit.
- `reports/trust_report.md`: Safety, trust, and deployment guidelines.
- `reports/intent_evaluation.md`: 5-model classifier comparison.
- `reports/retrieval_evaluation.md`: Dense vector retrieval benchmarks.
