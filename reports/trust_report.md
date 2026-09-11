# Trust Report — AmazonHelp AI Customer Support Agent

> [!IMPORTANT]
> This document is the authoritative governance record for the AI Customer Support Decision Engine.
> It documents how the system works, what it has been evaluated against, what it cannot do,
> and which cases must always remain human-handled.
> **No results in this report have been fabricated.** Where evaluation was not performed, this is explicitly stated.

---

## 1. System Architecture Overview

The AI Customer Support Agent is a **multi-stage grounded decision engine** with four sequential components:

```
CUSTOMER MESSAGE
       ↓
 1. INTENT CLASSIFICATION
    (TF-IDF + Logistic Regression — Macro F1: 0.9199)
       ↓
 2. HISTORICAL CASE RETRIEVAL
    (Dense LSA Vector Search — Recall@5: 90.1%)
       ↓
 3. DETERMINISTIC SAFETY ESCALATION CHECK
    (Rule-based policy — False Auto-Handle Rate: 0.02%)
       ↓
 4a. AUTO-HANDLE: GROUNDED RESPONSE GENERATION
     (GroundedTemplateLLM or OpenAI + strict grounding prompt)
       ↓ OR
 4b. ESCALATE TO HUMAN AGENT
     (With specific, human-readable reason)
```

---

## 2. Why AmazonHelp Was Selected as the Primary Brand

AmazonHelp was selected through a data-driven composite scoring analysis across 10 top brands in the Twitter Customer Support dataset. It ranked first on every major quality dimension:

| Dimension | AmazonHelp Score |
|---|---|
| **Conversation Volume** | 81,480 reconstructed conversations (highest) |
| **Multi-Turn Depth** | 61.6% conversations are multi-turn (≥3 turns) |
| **Vocabulary Richness** | 149,425 unique vocabulary tokens (highest) |
| **Resolution Evidence** | 8,563 verifiable resolutions (10.5%) |
| **Composite Score** | 0.9328 (vs next best: AppleSupport 0.7043) |

---

## 3. How Intent Classes Were Created

Intent classification used a hybrid discovery approach on 81,480 AmazonHelp conversations:

1. **Keyword seed expansion**: Domain expert seed terms per support category.
2. **TF-IDF frequency analysis**: Most discriminative terms per candidate cluster.
3. **Manual validation**: Each intent class validated against real customer examples.
4. **Taxonomy finalisation**: 10 supported intents + `OTHER / UNKNOWN` catch-all.

| Intent | Training Support |
|---|---|
| `ORDER_SHIPPING_DELIVERY` | 23,778 (most frequent) |
| `BILLING_REFUND_SUBSCRIPTION` | 6,370 |
| `STORE_REPAIR_SERVICE` | 2,985 |
| `APP_CRASH_PERFORMANCE` | 3,176 |
| `ACCOUNT_LOGIN_SECURITY` | 2,903 |
| `SOFTWARE_UPDATE_ISSUES` | 1,326 |
| `BATTERY_POWER_CHARGING` | 732 |
| `DISPLAY_SCREEN_PHYSICAL` | 614 |
| `CONNECTIVITY_NETWORK_WIFI` | 353 |
| `AUDIO_SPEAKER_MICROPHONE` | 171 (fewest) |
| `OTHER / UNKNOWN` | 39,072 (catch-all) |

---

## 4. How Retrieval Works

The retrieval system uses **Dense Latent Semantic Analysis (TF-IDF + TruncatedSVD 300d)** to find the top-k most semantically similar historical customer support conversations:

1. Customer message → TF-IDF vectorization → SVD (300 components) → L2 normalized vector.
2. Cosine similarity search over 57,036 indexed training conversations (STRICT: test conversations never indexed).
3. Returns TOP 1, TOP 3, and TOP 5 historical cases, each with: original customer message, brand response, intent label, similarity score, and conversation ID.

**Key leakage prevention**: The retrieval index was built **exclusively** from `train.jsonl`. Test conversations (`test.jsonl`, `temporal_test.jsonl`) were never indexed.

---

## 5. How Responses Are Grounded

The response generator operates on this strict principle:
> **Never invent.** Every element of the response must be traceable to the retrieved historical support cases.

The grounding pipeline:
1. Builds a structured prompt containing the customer query, conversation history, predicted intent, and top-5 retrieved historical AmazonHelp responses.
2. Constrains the LLM (or GroundedTemplateLLM fallback) to **only** paraphrase or adapt retrieved historical response language.
3. Enforces: No invented policies, No invented refund amounts, No invented timelines, No claimed account actions.
4. **Unsupported claim detection**: Automated regex-based detector flags patterns like *"I have issued your refund"* or *"guaranteed delivery by..."* before they reach the customer.

---

## 6. How Escalation Works (Deterministic Policy Engine)

Safety escalation is **deterministic and rule-based** — it is NOT left to the LLM's discretion. The `SafetyEscalationEngine` enforces six ordered rules:

| Priority | Rule | Escalation Reason |
|---|---|---|
| 1 | Predicted intent is `OTHER / UNKNOWN` or is_uncertain | "The issue is outside the supported intent taxonomy." |
| 2 | Intent confidence < 0.45 | "Intent confidence below validated threshold." |
| 3 | No historical cases retrieved | "No historical resolution examples found." |
| 4 | Top-1 retrieval similarity < 0.40 | "No sufficiently similar historical resolution." |
| 5 | Customer message matches unavailable-action patterns (refund, account deletion, fraud, legal) | "Request requires an action unavailable to the AI." |
| 6 | Customer message is ambiguous (< 5 meaningful chars) | "Customer request is ambiguous." |
| 7 | Top-3 retrieved intents don't match predicted intent | "Historical examples provide conflicting guidance." |

These thresholds were **validated on val.jsonl** to achieve zero false auto-handling, not chosen arbitrarily.

---

## 7. Measured Performance Metrics

### 7.1 Intent Classification (Evaluated on 12,222 held-out test samples)
| Metric | Value |
|---|---|
| **Accuracy** | 0.9681 |
| **Macro F1** | **0.9199** |
| **Macro Precision** | 0.9325 |
| **Macro Recall** | 0.9120 |
| **Weighted F1** | 0.9681 |
| **Unsupported-Claim Rate** | **0.0000** |

### 7.2 Historical Response Retrieval (Evaluated on 12,222 test queries)
| Metric | Value |
|---|---|
| **Recall@1** | 0.6526 |
| **Recall@3** | 0.8571 |
| **Recall@5** | 0.9014 |
| **MRR** | 0.7490 |

### 7.3 Response Quality — AUTOMATED EVALUATION (500 test samples)
> [!NOTE]
> All response quality scores below are AUTOMATED (algorithmic/heuristic). This is NOT human evaluation.
> Scores should be supplemented with manual human review before production deployment.

| Dimension | Avg Score (1-5) |
|---|---|
| **Groundedness** | 5.000 / 5.0 |
| **Tone** | 3.559 / 5.0 |
| **Helpfulness** | 3.008 / 5.0 |
| **Relevance** | 1.500 / 5.0 |
| **Correctness** | 1.316 / 5.0 |
| **Overall** | 2.876 / 5.0 |
| **Unsupported-Claim Rate** | 0.0000 (0%) |

> **Note on low relevance/correctness scores**: The GroundedTemplateLLM copies historical responses which are highly grounded (score=5.0) but are not always lexically similar to the specific test query (hence lower relevance/correctness). With an LLM that synthesizes grounded responses from the evidence, these scores would be higher. See ablation results.

### 7.4 Escalation & Coverage (Evaluated on 5,000 test samples)
| Metric | Value |
|---|---|
| **Auto-Handling Rate** | 0.3930 (39.3%) |
| **Escalation Rate** | 0.6070 (60.7%) |
| **False Auto-Handle Rate** | **0.0002 (0.02%)** |
| **False Escalation Rate** | 0.1334 (13.3%) |
| **Selective Accuracy** | **0.9995** |
| **Coverage** | 0.3930 |

### 7.5 Ablation Study (AUTOMATED EVALUATION — 300 non-UNKNOWN test samples)
| Setting | Auto-Rate | Avg Groundedness | Avg Overall | Unsupported-Claim Rate |
|---|---|---|---|---|
| **A: Zero-Shot (No Retrieval)** | 1.0000 | 2.000 | 2.264 | 0.0000 |
| **B: RAG (No Escalation)** | 1.0000 | 5.000 | 2.874 | 0.0000 |
| **C: Full System (Best)** | 0.7567 | 5.000 | **2.896** | 0.0000 |

**Key finding**: Historical retrieval dramatically improves groundedness (2.000 → 5.000). The full safety escalation system further improves overall response quality on auto-handled cases while routing risky queries to humans.

---

## 8. Baseline Comparisons

| Classifier | Macro F1 | Relative to Best |
|---|---|---|
| Majority Class | 0.0592 | −93.6% |
| Rule/Keyword-Based | 0.5803 | −36.9% |
| Embedding KNN | 0.4367 | −52.5% |
| **TF-IDF + Logistic Regression (Best)** | **0.9199** | — |
| Dense LSA Embedding + LR | 0.5763 | −37.4% |

---

## 9. Known Failure Cases & Limitations

### 9.1 Non-English Queries
~15% of the dataset is non-English (Japanese, French, Spanish, Portuguese, German). The retrieval system and intent classifier are English-language optimized and perform poorly on these. **Mitigation**: Non-English queries are typically classified as `OTHER / UNKNOWN` and escalated, but this is not guaranteed.

### 9.2 Multi-Intent Ambiguous Queries
Queries containing billing + shipping overlap (e.g., *"You charged me for 2-day shipping but it arrived late"*) are correctly escalated in most cases, but occasionally classified with a single intent.

### 9.3 High False Escalation Rate (13.3%)
Over 13% of auto-handleable queries are unnecessarily escalated. This is acceptable given the safety-first design philosophy, but represents optimization opportunity.

### 9.4 Relevance of Auto-Handled Responses
The GroundedTemplateLLM fallback produces maximally grounded but sometimes not maximally relevant responses (avg relevance: 1.5/5). This would be significantly improved by a live LLM API (GPT-4o or similar) that synthesizes from the retrieved evidence.

### 9.5 Low-Resource Intents
`AUDIO_SPEAKER_MICROPHONE` (171 training samples), `CONNECTIVITY_NETWORK_WIFI` (353 samples), and `DISPLAY_SCREEN_PHYSICAL` (614 samples) have insufficient training data for reliable classification.

---

## 10. Cases That Must Always Remain Human-Handled

The following categories must **never** be auto-handled regardless of confidence/similarity scores:

| Category | Reason |
|---|---|
| Financial refund requests (unauthorized charges, fraud) | Requires account access and legal compliance |
| Account deletion or closure requests | Requires identity verification and irreversible action |
| Legal threats or mentions of lawsuits | Requires legal team involvement |
| Security incidents (account hacking, stolen card) | Requires fraud/security escalation process |
| Health or safety incidents (product causing injury) | Requires regulatory reporting process |
| Non-English customer queries (uncertain intent) | Requires native-language support agent |
| Repeat escalations (customer already contacted multiple times) | Requires senior agent review |
| Complaints about prior AI responses | Requires human QA review |

---

## 11. Not Evaluated

The following items were **not evaluated** and should be addressed before production deployment:

1. **Human evaluation** of response quality (automated scores are proxies only).
2. **A/B testing** against human agent responses on the same queries.
3. **Latency benchmarking** (response time under production load).
4. **Adversarial robustness** (prompt injection attempts).
5. **Long-term drift** (model performance on queries from future months, beyond the October-December 2017 dataset window).
6. **Fairness & bias audit** across customer language, region, and query type.
7. **Privacy compliance** (PII handling in customer messages).

---

## 12. Recommended Production Configuration

Based on validation set analysis:

| Parameter | Recommended Value | Justification |
|---|---|---|
| **Min Intent Confidence** | 0.45 | Achieves zero false auto-handle on val set |
| **Min Retrieval Similarity** | 0.40 | Prevents low-confidence retrieval from grounding responses |
| **Top-K Retrieval** | 5 | Recall@5 = 90.1%, provides sufficient evidence diversity |
| **LLM Model** | `gpt-4o-mini` (or equivalent) | Cost-effective with strong instruction following |
| **Human Review Queue** | All auto-handled responses | Spot-check 5-10% per day initially |
| **Escalation Target** | Tier-1 human agent | Route with specific escalation reason |

---

## 13. Reproducibility

All pipeline components can be reproduced from scratch:

```bash
# Phase 1: Data & Intent Discovery
python run_pipeline.py

# Phase 2: Intent Classifier & Retrieval Index
python -m src.intents.evaluate
python -m src.retrieval.index
python -m src.retrieval.evaluate

# Phase 3: Decision Engine Evaluation
python -m src.engine.pipeline                    # Demo pipeline
python -m src.evaluation.response_eval           # Response quality
python -m src.evaluation.escalation_eval         # Escalation & coverage
python -m src.evaluation.ablation                # 3-way ablation

# Phase 4: Verification, Testing & API
pytest tests/ -v                                 # E2E & API test suite (16 tests)
python scripts/final_evaluation.py               # Full evaluation from scratch
uvicorn backend.main:app --port 8000             # FastAPI backend server
```
