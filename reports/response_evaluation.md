# Response Quality Evaluation Report

> [!NOTE]
> All evaluation in this report is **AUTOMATED** using algorithmic/heuristic scoring.
> This is **NOT human evaluation**. Scores are approximate and should be
> supplemented with manual review before production deployment.

## Overview
- **Total test samples evaluated**: 500
- **Auto-handled**: 374 (74.8%)
- **Escalated**: 126 (25.2%)
- **Unsupported-Claim Rate** (auto-handled only): 0.0000 (0.00%)

## Automated Quality Rubric Scores (1-5 Scale, Auto-Handled Responses Only)
| Dimension | Average Score (1-5) | Description |
|---|---|---|
| **Groundedness** | **5.000** ⭐⭐⭐⭐⭐ | Lexical overlap between reply and historical evidence |
| **Relevance** | **1.500** ⭐⭐ | Keyword & semantic match to customer message + intent |
| **Tone** | **3.559** ⭐⭐⭐⭐ | Professional, empathetic tone markers |
| **Correctness** | **1.316** ⭐ | Similarity to true historical brand response |
| **Helpfulness** | **3.008** ⭐⭐⭐ | Composite of groundedness, relevance, tone |
| **Overall** | **2.876** ⭐⭐⭐ | Mean across all rubric dimensions |

## Per-Intent Average Overall Score
| Intent | Avg Score | Sample Count |
|---|---|---|
| `ACCOUNT_LOGIN_SECURITY` | 2.916 | 19 |
| `APP_CRASH_PERFORMANCE` | 2.730 | 23 |
| `BATTERY_POWER_CHARGING` | 2.600 | 1 |
| `BILLING_REFUND_SUBSCRIPTION` | 2.854 | 56 |
| `DISPLAY_SCREEN_PHYSICAL` | 2.333 | 6 |
| `ORDER_SHIPPING_DELIVERY` | 2.930 | 235 |
| `SOFTWARE_UPDATE_ISSUES` | 2.760 | 5 |
| `STORE_REPAIR_SERVICE` | 2.717 | 29 |

## Evaluation Rubric Definition
| Score | Meaning |
|---|---|
| **5** | Excellent — Fully grounded, relevant, professional, matches historical patterns |
| **4** | Good — Mostly grounded and relevant with minor gaps |
| **3** | Acceptable — Partially grounded; some gaps in relevance or tone |
| **2** | Poor — Weak grounding or low relevance; needs human review |
| **1** | Failing — Not grounded, irrelevant, or empty |

## Reproducibility
```bash
python -m src.evaluation.response_eval
```