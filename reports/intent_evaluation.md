# Intent Classification Evaluation Report

## Executive Summary
This report presents a rigorous comparative evaluation of **5 Intent Classification models** on held-out customer support data.
The top-performing classifier is **`Proposed Model A: TF-IDF + Logistic Regression`**, achieving a **Test Macro F1-Score of 0.9199** and **Test Accuracy of 0.9681**.

## Classifier Comparison Table (Evaluated on Held-Out Test Set)
| Model Approach | Accuracy | Macro Precision | Macro Recall | Macro F1 | Weighted F1 | Fit Time (s) |
|---|---|---|---|---|---|---|
| `Baseline 1: Majority Class` | 0.4830 | 0.0439 | 0.0909 | **0.0592** | 0.3146 | 0.0 |
| `Baseline 2: Rule / Keyword-Based` | 0.8067 | 0.7398 | 0.5593 | **0.5803** | 0.7719 | 0.0 |
| `Baseline 3: Embedding Nearest-Neighbor (KNN)` | 0.6396 | 0.5417 | 0.4425 | **0.4367** | 0.6176 | 19.4 |
| `Proposed Model A: TF-IDF + Logistic Regression` **(Best)** | 0.9681 | 0.9325 | 0.9120 | **0.9199** | 0.9681 | 10.4 |
| `Proposed Model B: Dense Embedding + Logistic Regression` | 0.7982 | 0.5834 | 0.6409 | **0.5763** | 0.8231 | 36.3 |

## Baseline vs Proposed Model Improvements
- **Improvement over Majority Class**: +0.8607 Macro F1 increase.
- **Improvement over Keyword/Rule Baseline**: +58.52% relative Macro F1 gain.
- **Improvement over Simple KNN Embedding Baseline**: +110.65% relative Macro F1 gain.

## Best Classifier Per-Intent Detailed Metrics (`Proposed Model A: TF-IDF + Logistic Regression`)
| Intent Class | Support Count | Precision | Recall | F1-Score |
|---|---|---|---|---|
| `ACCOUNT_LOGIN_SECURITY` | 414 | 0.9351 | 0.9396 | **0.9373** |
| `APP_CRASH_PERFORMANCE` | 470 | 0.9287 | 0.9426 | **0.9356** |
| `AUDIO_SPEAKER_MICROPHONE` | 24 | 1.0000 | 0.8750 | **0.9333** |
| `BATTERY_POWER_CHARGING` | 108 | 0.9307 | 0.8704 | **0.8995** |
| `BILLING_REFUND_SUBSCRIPTION` | 943 | 0.9483 | 0.9523 | **0.9503** |
| `CONNECTIVITY_NETWORK_WIFI` | 50 | 0.9524 | 0.8000 | **0.8696** |
| `DISPLAY_SCREEN_PHYSICAL` | 86 | 0.7800 | 0.9070 | **0.8387** |
| `ORDER_SHIPPING_DELIVERY` | 3,549 | 0.9882 | 0.9425 | **0.9648** |
| `OTHER / UNKNOWN` | 5,903 | 0.9799 | 0.9990 | **0.9893** |
| `SOFTWARE_UPDATE_ISSUES` | 197 | 0.9649 | 0.8376 | **0.8967** |
| `STORE_REPAIR_SERVICE` | 478 | 0.8493 | 0.9665 | **0.9041** |

## Confusion Matrix (Test Data)
| True \ Pred | ACCOUNT | APP | AUDIO | BATTERY | BILLING | CONNECTIVITY | DISPLAY | ORDER | OTHER / UNKNOWN | SOFTWARE | STORE |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ACCOUNT | 389 | 4 | 0 | 0 | 1 | 1 | 3 | 9 | 4 | 0 | 3 |
| APP | 0 | 443 | 0 | 0 | 4 | 0 | 2 | 5 | 6 | 1 | 9 |
| AUDIO | 0 | 0 | 21 | 0 | 0 | 0 | 0 | 0 | 3 | 0 | 0 |
| BATTERY | 4 | 2 | 0 | 94 | 1 | 0 | 0 | 2 | 4 | 0 | 1 |
| BILLING | 6 | 1 | 0 | 1 | 898 | 0 | 4 | 15 | 9 | 0 | 9 |
| CONNECTIVITY | 0 | 0 | 0 | 0 | 0 | 40 | 0 | 0 | 9 | 0 | 1 |
| DISPLAY | 0 | 0 | 0 | 0 | 0 | 0 | 78 | 0 | 5 | 0 | 3 |
| ORDER | 14 | 16 | 0 | 5 | 33 | 1 | 11 | 3345 | 65 | 5 | 54 |
| OTHER / UNKNOWN | 1 | 0 | 0 | 0 | 3 | 0 | 0 | 2 | 5897 | 0 | 0 |
| SOFTWARE | 2 | 10 | 0 | 0 | 5 | 0 | 2 | 6 | 5 | 165 | 2 |
| STORE | 0 | 1 | 0 | 1 | 2 | 0 | 0 | 1 | 11 | 0 | 462 |

## Confidence Scoring & UNKNOWN / UNCERTAIN Handling
- The classifier produces explicit probability distributions and confidence scores for every message.
- If max predicted confidence falls below the calibrated threshold (0.40), the message is flagged as `is_uncertain: true` and mapped to `OTHER / UNKNOWN` to prevent forced false positive predictions.

## Reproducibility Commands
```bash
python -m src.intents.evaluate
```