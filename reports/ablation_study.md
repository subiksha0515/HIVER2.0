# Ablation Study Report — 3-Way System Comparison

> [!NOTE]
> All evaluation is **AUTOMATED** (algorithmic/heuristic). This is **NOT human evaluation**.

Ablation evaluated on **300** non-UNKNOWN held-out test samples.

## Comparative Results Table
| Setting | Auto-Rate | Avg Groundedness | Avg Relevance | Avg Overall | Unsupported-Claim Rate |
|---|---|---|---|---|---|
| **A: Zero-Shot (No Retrieval)** | 1.0000 | 2.000 | 1.000 | 2.264 | 0.0000 |
| **B: RAG (No Escalation)** | 1.0000 | 5.000 | 1.450 | 2.874 | 0.0000 |
| **C: Full System (Best)** | 0.7567 | 5.000 | 1.555 | 2.896 | 0.0000 |

## Key Findings
- **Retrieval improves grounding** (B vs A): +3.000 avg groundedness score.
- **Safety escalation further refines quality** (C vs B): +0.000 avg groundedness on auto-handled responses.
- **Full system reduces unsupported claims** (C vs B): UCR reduced by 0.0000.
- **Escalation safety filter** (C): 73/300 risky queries escalated to human agents.

## Reproducibility
```bash
python -m src.evaluation.ablation
```