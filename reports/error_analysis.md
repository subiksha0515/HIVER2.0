# Error Analysis Report — AI Customer Support Agent (Phase 3)

## Overview

This report documents failure modes observed in the AI Customer Support Decision Engine
evaluated on held-out test data (`test.jsonl`). The analysis covers:
- Wrong intent predictions
- Bad retrieval results
- Hallucinated / unsupported claim patterns
- False auto-handling cases
- Unnecessary escalation cases

---

## 1. Wrong Intent Predictions

### Most Confused Intent Pairs (From Phase 2 Confusion Matrix)
| True Intent | Predicted As | Misclassification Count |
|---|---|---|
| `ORDER_SHIPPING_DELIVERY` | `BILLING_REFUND_SUBSCRIPTION` | 33 |
| `ORDER_SHIPPING_DELIVERY` | `STORE_REPAIR_SERVICE` | 54 |
| `SOFTWARE_UPDATE_ISSUES` | `APP_CRASH_PERFORMANCE` | 10 |
| `BATTERY_POWER_CHARGING` | `ACCOUNT_LOGIN_SECURITY` | 4 |
| `CONNECTIVITY_NETWORK_WIFI` | `OTHER / UNKNOWN` | 9 |

### Root Causes
1. **Order/Billing Overlap**: Customer messages about missing packages that include payment disputes (e.g. *"I paid for 2-day shipping and it didn't arrive — give me a refund"*) lexically span both `ORDER_SHIPPING_DELIVERY` and `BILLING_REFUND_SUBSCRIPTION`. The TF-IDF classifier assigns the primary intent based on term frequency, which may not always match the dominant user concern.
2. **Software/App Overlap**: Messages like *"the app crashes after the update"* contain both `APP_CRASH_PERFORMANCE` and `SOFTWARE_UPDATE_ISSUES` signals. The classifier defaults to the higher-frequency intent.
3. **Low-Resource Intents**: `AUDIO_SPEAKER_MICROPHONE` (171 training samples), `CONNECTIVITY_NETWORK_WIFI` (353), and `DISPLAY_SCREEN_PHYSICAL` (614) have limited training data, making them prone to misclassification as `OTHER / UNKNOWN`.

---

## 2. Bad Retrieval Cases

### Pattern 1: Non-English Queries
Customer messages in Japanese, Portuguese, French, or other non-English languages receive low cosine similarity scores because the TF-IDF vocabulary is English-dominated. Retrieval falls back to high-frequency stopword matches.

**Example**: Japanese query about Amazon Prime subscription cancellation retrieved an English shipping query.

### Pattern 2: Short / Ambiguous Messages
Messages like *"@AmazonHelp help me"* or *"what the hell"* are too short for meaningful vector matching. Retrieval returns high similarity to other short queries, not topically related ones.

### Pattern 3: Cross-Intent Confusion
A billing query that mentions delivery terms (*"I paid for 2-day shipping"*) retrieves ORDER_SHIPPING_DELIVERY examples because shipping terms dominate the TF-IDF vector, even though the core concern is billing.

### Pattern 4: URL/Handle Noise
Twitter-style messages composed largely of URLs (`https://t.co/...`) and handles (`@115821`) produce TF-IDF vectors where meaningful content tokens are diluted by noise tokens, degrading retrieval quality.

---

## 3. Hallucination & Unsupported Claim Patterns

### Risk Category A: Promise of Action
The GroundedTemplateLLM is deterministic and copies historical response text. However, historical responses occasionally contain soft commitments like *"we'll contact you soon"* which is acceptable as it's a historical support behavior, not a fabricated promise.

The automated Unsupported-Claim detector flags patterns such as:
- *"I have issued your refund"* — Direct fabricated action claim
- *"Your order has been cancelled"* — Fabricated status update
- *"Guaranteed delivery by..."* — Fabricated timeline

**Mitigation**: The `COMPILED_CLAIM_PATTERNS` regex list in `response_eval.py` detects these patterns before they reach the customer.

### Risk Category B: Policy Invention
Without strict grounding constraints, LLMs may invent *"Amazon's policy states that..."* statements unsupported by the retrieved evidence. The system prompt explicitly forbids this.

---

## 4. False Auto-Handle Cases

### Observed Count
- On 5,000 test samples: **1 false auto-handle** (False Auto-Handle Rate: **0.0002**)
- This is exceptionally low and meets the safety requirement.

### Root Cause of the 1 False Auto-Handle
The one case involved a query classified with high intent confidence (> 0.45) and high retrieval similarity (> 0.40), but the true label was `OTHER / UNKNOWN` due to an ambiguous customer message. The classifier incorrectly assigned a high-confidence intent label because the message contained strong domain keywords.

**Mitigation**: The escalation engine's ambiguity pattern check (`len(clean_msg) < 5`) could be expanded to cover borderline ambiguous messages. This is recommended for production.

---

## 5. Unnecessary Escalation Cases

### Observed Count
- On 5,000 test samples: **667 unnecessary escalations** (False Escalation Rate: **0.1334**)
- Many of these are intent-labeled queries from the test set that were technically resolvable but escalated due to `OTHER / UNKNOWN` intent assignment.

### Root Causes
1. **Conservative `OTHER / UNKNOWN` Label**: ~48% of training data is `OTHER / UNKNOWN`. Any query classified as `OTHER / UNKNOWN` triggers escalation, which is correct for safety but over-conservative for edge cases.
2. **Retrieval Similarity Threshold**: Some genuinely similar queries fall just below the similarity threshold (e.g., 0.37 vs 0.40), triggering unnecessary escalation.
3. **Low-Resource Intent Classes**: Minority intents (e.g., `AUDIO_SPEAKER_MICROPHONE` with 171 training samples) are sometimes misclassified as `OTHER / UNKNOWN`, unnecessarily escalating audio-related queries.

### Mitigation Recommendations
- Fine-tune the `OTHER / UNKNOWN` boundary using active learning on mis-escalated examples.
- Implement a *"second opinion"* retrieval step before escalation: if top retrieval similarity is > 0.65, allow auto-handle even for borderline confidence scores.

---

## 6. Summary Table

| Failure Mode | Frequency | Severity | Mitigation Status |
|---|---|---|---|
| Wrong intent (Order/Billing overlap) | Moderate | Medium | Partially mitigated by high overall F1 (0.92) |
| Wrong intent (low-resource classes) | Low | Medium | Needs more labeled training data |
| Bad retrieval (non-English) | Low | Low | Escalated by low similarity threshold |
| Bad retrieval (short messages) | Moderate | Low | Caught by ambiguity rule in escalation engine |
| Unsupported claim in response | Very Low | **High** | Detected by `detect_unsupported_claims()` regex |
| False auto-handle | Extremely Low (0.02%) | **Critical** | 1 case on 5,000; acceptable but monitored |
| False escalation | Moderate (13.3%) | Low | Conservative by design; safety first |

---

## Recommendations for Production

1. **Expand ambiguity detection rules** to cover message length < 10 chars and queries with >50% URL/handle tokens.
2. **Add non-English detection**: Escalate non-English queries immediately (they cannot be reliably grounded in English-language historical data).
3. **Monitor false auto-handle rate continuously** with a human review queue for all auto-handled queries.
4. **Retrain with augmented low-resource intents** (AUDIO, CONNECTIVITY, DISPLAY) with at least 500+ labeled examples each.
5. **Second-opinion retrieval step**: Before escalating borderline cases, check if top-3 retrieved responses all share the predicted intent — if so, proceed to auto-handle.
