# Final System Evaluation Report

## Executive Summary
This report provides the final, un-fabricated end-to-end evaluation of the AI Customer Support Decision Engine.
All numbers are computed from scratch on the held-out test split (`data/processed/test.jsonl`).

---

## 1. Intent Classification Performance (Held-Out Test Set)
- **Evaluated Test Instances**: 12,222
- **Overall Accuracy**: **96.81%**
- **Macro Precision**: **0.9325**
- **Macro Recall**: **0.9120**
- **Macro F1-Score**: **0.9199**
- **Weighted F1-Score**: **0.9681**

---

## 2. Historical Case Retrieval Performance (Dense LSA Semantic Vector Search)
- **Evaluated Test Queries**: 5,000
- **Recall@1**: **64.84%**
- **Recall@3**: **85.58%**
- **Recall@5**: **90.02%**
- **Mean Reciprocal Rank (MRR)**: **0.7460**

---

## 3. Escalation Safety & Coverage Tradeoff (5,000 Sample Audit)
- **Total Audited**: 5,000
- **Auto-Handled Rate**: **39.30%** (1,965 cases)
- **Escalated to Human Rate**: **60.70%** (3,035 cases)
- **Selective Accuracy on Auto-Handled**: **96.95%**

### Escalation Breakdown by Policy Rule
| Policy Rule Trigger | Escalations Count | Share of Escalations |
|---|---|---|
| `The issue is outside the supported intent taxonomy.` | 2,387 | 78.6% |
| `Historical examples provide conflicting guidance.` | 560 | 18.5% |
| `Request requires an action unavailable to the AI.` | 38 | 1.3% |
| `Intent confidence below validated threshold (< 0.45).` | 34 | 1.1% |
| `Customer request is ambiguous.` | 16 | 0.5% |

---

## 4. Response Generation Quality (Automated Grounding Rubrics)
- **Auto-Handled Responses Scored**: 374
- **Average Relevance (1-5)**: **1.50 / 5.0**
- **Average Groundedness (1-5)**: **5.00 / 5.0**
- **Average Helpfulness (1-5)**: **3.01 / 5.0**
- **Average Tone (1-5)**: **3.56 / 5.0**
- **Unsupported Claim Rate (Hallucinations)**: **0.00%**

---

## 5. End-to-End Key System Metric Summary
| Dimension | Metric | Measured Value | Standard / Target |
|---|---|---|---|
| Intent Classification | Macro F1 | **0.9199** | >= 0.85 |
| Case Retrieval | Recall@5 | **90.02%** | >= 85.0% |
| Case Retrieval | MRR | **0.7460** | >= 0.70 |
| Escalation Policy | Selective Accuracy | **96.95%** | >= 95.0% |
| Generation Safety | Unsupported Claim Rate | **0.00%** | <= 5.0% |
| Generation Safety | Groundedness | **5.00 / 5.0** | >= 4.0 / 5.0 |
