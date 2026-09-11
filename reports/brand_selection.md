# Brand Selection Report - Twitter Customer Support Agent

## Executive Summary
Based on rigorous quantitative evaluation across volume, multi-turn dialogue depth, vocabulary/issue diversity, and resolution evidence rates, **`AmazonHelp`** has been selected as the single primary brand for building the AI Customer Support Agent pipeline.

## Top Brand Candidates Comparison Table
| Rank | Brand Handle | Total Conversations | Multi-Turn (>=3 turns) | Multi-Turn % | Avg Turns | Vocabulary Size | Composite Score |
|---|---|---|---|---|---|---|---|
| 1 | `AmazonHelp` | 81,480 | 50,184 | 61.6% | 4.51 | 149,425 | 0.9328 |
| 2 | `AppleSupport` | 80,438 | 27,865 | 34.6% | 2.92 | 88,295 | 0.7043 |
| 3 | `Uber_Support` | 41,814 | 14,979 | 35.8% | 3.04 | 57,570 | 0.3969 |
| 4 | `AmericanAir` | 25,971 | 11,162 | 43.0% | 3.26 | 54,423 | 0.3030 |
| 5 | `Delta` | 25,938 | 10,918 | 42.1% | 3.29 | 50,655 | 0.2988 |
| 6 | `SpotifyCares` | 28,192 | 10,415 | 36.9% | 3.23 | 42,094 | 0.2961 |
| 7 | `Tesco` | 16,550 | 11,457 | 69.2% | 4.24 | 41,047 | 0.2606 |
| 8 | `comcastcares` | 23,853 | 8,584 | 36.0% | 2.99 | 38,528 | 0.2437 |
| 9 | `SouthwestAir` | 21,409 | 7,006 | 32.7% | 2.8 | 44,842 | 0.2395 |
| 10 | `TMobileHelp` | 22,563 | 8,370 | 37.1% | 3.52 | 36,604 | 0.2357 |

## Selection Criteria & Data-Driven Rationale for `AmazonHelp`

1. **High Conversation Volume**: `AmazonHelp` accounts for **81,480** reconstructed customer-support conversations, providing a rich, high-density sample for intent discovery and model training.
2. **Substantial Multi-Turn Depth**: Contains **50,184** multi-turn interaction threads (61.6% of conversations), ensuring the agent can learn multi-turn dialogue state tracking and context retention.
3. **Broad Issue & Vocabulary Variety**: A vocabulary size of **149,425** unique words in customer inquiries reflects a wide range of customer problems (e.g. software updates, hardware issues, account inquiries, billing, app performance).
4. **Resolution Evidence**: Provides **8,563** conversations (10.5%) with verifiable resolution evidence.

## Pipeline Integration
All subsequent Phase 1 steps (Intent Discovery, Intent Taxonomy, and Leakage-Safe Data Splits) will operate on conversations specifically corresponding to `AmazonHelp`.
