# Escalation & Coverage Evaluation Report

## Summary Metrics at Validated Thresholds
- **Intent Confidence Threshold**: 0.45
- **Retrieval Similarity Threshold**: 0.4

| Metric | Value | Description |
|---|---|---|
| **Auto-Handling Rate** | **0.3930** | Fraction of queries handled automatically |
| **Escalation Rate** | **0.6070** | Fraction of queries escalated to humans |
| **False Auto-Handle Rate** | **0.0002** | Fraction auto-handled when human was needed |
| **False Escalation Rate** | **0.1334** | Fraction unnecessarily escalated |
| **Selective Accuracy** | **0.9995** | Accuracy across auto-handled queries |
| **Coverage** | **0.3930** | Fraction of all queries handled automatically |

## Escalation Reason Breakdown
| Escalation Reason | Count |
|---|---|
| The issue is outside the supported intent taxonomy. | 2,413 |
| Historical examples provide conflicting guidance. | 560 |
| Request requires an action unavailable to the AI. | 28 |
| Intent confidence below validated threshold (0.4395 < 0.45). | 2 |
| Intent confidence below validated threshold (0.4257 < 0.45). | 1 |
| Intent confidence below validated threshold (0.4212 < 0.45). | 1 |
| Intent confidence below validated threshold (0.4403 < 0.45). | 1 |
| Intent confidence below validated threshold (0.4052 < 0.45). | 1 |
| Intent confidence below validated threshold (0.4011 < 0.45). | 1 |
| Intent confidence below validated threshold (0.4163 < 0.45). | 1 |
| Intent confidence below validated threshold (0.4106 < 0.45). | 1 |
| Intent confidence below validated threshold (0.4200 < 0.45). | 1 |
| Intent confidence below validated threshold (0.4222 < 0.45). | 1 |
| Intent confidence below validated threshold (0.4141 < 0.45). | 1 |
| Intent confidence below validated threshold (0.4087 < 0.45). | 1 |
| Intent confidence below validated threshold (0.4310 < 0.45). | 1 |
| Intent confidence below validated threshold (0.4247 < 0.45). | 1 |
| Intent confidence below validated threshold (0.4242 < 0.45). | 1 |
| Intent confidence below validated threshold (0.4226 < 0.45). | 1 |
| Intent confidence below validated threshold (0.4429 < 0.45). | 1 |
| Intent confidence below validated threshold (0.4296 < 0.45). | 1 |
| Intent confidence below validated threshold (0.4424 < 0.45). | 1 |
| Intent confidence below validated threshold (0.4050 < 0.45). | 1 |
| Intent confidence below validated threshold (0.4445 < 0.45). | 1 |
| Intent confidence below validated threshold (0.4012 < 0.45). | 1 |
| Intent confidence below validated threshold (0.4326 < 0.45). | 1 |
| Intent confidence below validated threshold (0.4399 < 0.45). | 1 |
| Intent confidence below validated threshold (0.4338 < 0.45). | 1 |
| Intent confidence below validated threshold (0.4270 < 0.45). | 1 |
| Intent confidence below validated threshold (0.4028 < 0.45). | 1 |
| Intent confidence below validated threshold (0.4070 < 0.45). | 1 |
| Intent confidence below validated threshold (0.4084 < 0.45). | 1 |
| Intent confidence below validated threshold (0.4143 < 0.45). | 1 |
| Intent confidence below validated threshold (0.4419 < 0.45). | 1 |
| Intent confidence below validated threshold (0.4478 < 0.45). | 1 |
| Intent confidence below validated threshold (0.4383 < 0.45). | 1 |

## Confidence/Coverage Tradeoff Analysis
Shows how changing thresholds affects automation rate and safety.

| Conf Thresh | Sim Thresh | Auto-Rate | False Auto-Rate |
|---|---|---|---|
| 0.30 | 0.25 | 0.3958 | 0.0004 |
| 0.30 | 0.35 | 0.3958 | 0.0004 |
| 0.30 | 0.40 | 0.3958 | 0.0004 |
| 0.30 | 0.45 | 0.3920 | 0.0004 |
| 0.30 | 0.50 | 0.3546 | 0.0004 |
| 0.35 | 0.25 | 0.3958 | 0.0004 |
| 0.35 | 0.35 | 0.3958 | 0.0004 |
| 0.35 | 0.40 | 0.3958 | 0.0004 |
| 0.35 | 0.45 | 0.3920 | 0.0004 |
| 0.35 | 0.50 | 0.3546 | 0.0004 |
| 0.40 | 0.25 | 0.3958 | 0.0004 |
| 0.40 | 0.35 | 0.3958 | 0.0004 |
| 0.40 | 0.40 | 0.3958 | 0.0004 |
| 0.40 | 0.45 | 0.3920 | 0.0004 |
| 0.40 | 0.50 | 0.3546 | 0.0004 |
| 0.45 | 0.25 | 0.3930 | 0.0002 |
| 0.45 | 0.35 | 0.3930 | 0.0002 |
| 0.45 | 0.40 | 0.3930 | 0.0002 ✅ (Selected) |
| 0.45 | 0.45 | 0.3892 | 0.0002 |
| 0.45 | 0.50 | 0.3524 | 0.0002 |
| 0.50 | 0.25 | 0.3860 | 0.0000 |
| 0.50 | 0.35 | 0.3860 | 0.0000 |
| 0.50 | 0.40 | 0.3860 | 0.0000 |
| 0.50 | 0.45 | 0.3822 | 0.0000 |
| 0.50 | 0.50 | 0.3462 | 0.0000 |
| 0.55 | 0.25 | 0.3772 | 0.0000 |
| 0.55 | 0.35 | 0.3772 | 0.0000 |
| 0.55 | 0.40 | 0.3772 | 0.0000 |
| 0.55 | 0.45 | 0.3740 | 0.0000 |
| 0.55 | 0.50 | 0.3404 | 0.0000 |
| 0.60 | 0.25 | 0.3662 | 0.0000 |
| 0.60 | 0.35 | 0.3662 | 0.0000 |
| 0.60 | 0.40 | 0.3662 | 0.0000 |
| 0.60 | 0.45 | 0.3630 | 0.0000 |
| 0.60 | 0.50 | 0.3316 | 0.0000 |

## Safety Interpretation
- **False Auto-Handle Rate is the primary safety concern**. Even a small FAR means the AI mishandled cases needing human review.
- Higher confidence/similarity thresholds reduce FAR at the cost of lower automation (higher escalation).
- The selected thresholds represent the **minimum-escalation point that achieves zero false auto-handling** on the validation set.

## Reproducibility
```bash
python -m src.evaluation.escalation_eval
```