import json
import pandas as pd
from pathlib import Path
from typing import List, Dict, Any, Tuple

def analyze_and_select_brand(conversations: List[Dict[str, Any]], output_report_path: str = "reports/brand_selection.md") -> Tuple[str, Dict[str, Any]]:
    """
    Data-driven brand selection analysis across all reconstructed conversations.
    Outputs reports/brand_selection.md and returns selected brand name.
    """
    print(f"[brand_selection] Analyzing brand distribution across {len(conversations):,} conversations...")
    
    brand_stats = {}
    for c in conversations:
        brand = c['brand']
        if brand not in brand_stats:
            brand_stats[brand] = {
                'brand': brand,
                'total_conversations': 0,
                'multi_turn_convs': 0,
                'total_turns': 0,
                'resolutions_count': 0,
                'customer_vocab': set()
            }
        
        brand_stats[brand]['total_conversations'] += 1
        brand_stats[brand]['total_turns'] += c['turns']
        if c['turns'] >= 3:
            brand_stats[brand]['multi_turn_convs'] += 1
        if c['resolution_available']:
            brand_stats[brand]['resolutions_count'] += 1
            
        # Extract words from customer messages for issue variety
        words = c['customer_message'].lower().split()
        brand_stats[brand]['customer_vocab'].update(words)

    metrics_list = []
    for b, s in brand_stats.items():
        if s['total_conversations'] < 50:  # Filter minor brands
            continue
        vocab_size = len(s['customer_vocab'])
        avg_turns = round(s['total_turns'] / s['total_conversations'], 2)
        multi_turn_pct = round((s['multi_turn_convs'] / s['total_conversations']) * 100, 1)
        res_pct = round((s['resolutions_count'] / s['total_conversations']) * 100, 1)
        
        metrics_list.append({
            'brand': b,
            'total_conversations': s['total_conversations'],
            'multi_turn_convs': s['multi_turn_convs'],
            'multi_turn_pct': multi_turn_pct,
            'avg_turns': avg_turns,
            'resolutions_count': s['resolutions_count'],
            'res_pct': res_pct,
            'vocab_size': vocab_size
        })

    df_metrics = pd.DataFrame(metrics_list)
    if df_metrics.empty:
        raise ValueError("No brands found with >= 50 conversations.")

    # Calculate composite score for data-driven selection
    # Normalization: max-min scaling
    df_metrics['score_vol'] = df_metrics['total_conversations'] / df_metrics['total_conversations'].max()
    df_metrics['score_multi'] = df_metrics['multi_turn_convs'] / df_metrics['multi_turn_convs'].max()
    df_metrics['score_vocab'] = df_metrics['vocab_size'] / df_metrics['vocab_size'].max()
    df_metrics['score_res'] = df_metrics['res_pct'] / df_metrics['res_pct'].max()

    df_metrics['composite_score'] = (
        0.40 * df_metrics['score_vol'] +
        0.30 * df_metrics['score_multi'] +
        0.20 * df_metrics['score_vocab'] +
        0.10 * df_metrics['score_res']
    )

    df_sorted = df_metrics.sort_values(by='composite_score', ascending=False).reset_index(drop=True)
    selected_row = df_sorted.iloc[0]
    selected_brand = selected_row['brand']

    print(f"[brand_selection] Selected brand: '{selected_brand}' with composite score {selected_row['composite_score']:.4f}")

    # Generate reports/brand_selection.md
    Path(output_report_path).parent.mkdir(parents=True, exist_ok=True)
    report_content = f"""# Brand Selection Report - Twitter Customer Support Agent

## Executive Summary
Based on rigorous quantitative evaluation across volume, multi-turn dialogue depth, vocabulary/issue diversity, and resolution evidence rates, **`{selected_brand}`** has been selected as the single primary brand for building the AI Customer Support Agent pipeline.

## Top Brand Candidates Comparison Table
| Rank | Brand Handle | Total Conversations | Multi-Turn (>=3 turns) | Multi-Turn % | Avg Turns | Vocabulary Size | Composite Score |
|---|---|---|---|---|---|---|---|
"""
    for idx, row in df_sorted.head(10).iterrows():
        report_content += f"| {idx+1} | `{row['brand']}` | {row['total_conversations']:,} | {row['multi_turn_convs']:,} | {row['multi_turn_pct']}% | {row['avg_turns']} | {row['vocab_size']:,} | {row['composite_score']:.4f} |\n"

    report_content += f"""
## Selection Criteria & Data-Driven Rationale for `{selected_brand}`

1. **High Conversation Volume**: `{selected_brand}` accounts for **{selected_row['total_conversations']:,}** reconstructed customer-support conversations, providing a rich, high-density sample for intent discovery and model training.
2. **Substantial Multi-Turn Depth**: Contains **{selected_row['multi_turn_convs']:,}** multi-turn interaction threads ({selected_row['multi_turn_pct']}% of conversations), ensuring the agent can learn multi-turn dialogue state tracking and context retention.
3. **Broad Issue & Vocabulary Variety**: A vocabulary size of **{selected_row['vocab_size']:,}** unique words in customer inquiries reflects a wide range of customer problems (e.g. software updates, hardware issues, account inquiries, billing, app performance).
4. **Resolution Evidence**: Provides **{selected_row['resolutions_count']:,}** conversations ({selected_row['res_pct']}%) with verifiable resolution evidence.

## Pipeline Integration
All subsequent Phase 1 steps (Intent Discovery, Intent Taxonomy, and Leakage-Safe Data Splits) will operate on conversations specifically corresponding to `{selected_brand}`.
"""

    with open(output_report_path, "w", encoding="utf-8") as f:
        f.write(report_content)
        
    print(f"[brand_selection] Brand selection report saved to {output_report_path}")
    return selected_brand, selected_row.to_dict()

if __name__ == "__main__":
    from load_data import load_raw_dataset
    from clean_dataset import preprocess_dataset
    from conversations import reconstruct_conversations
    
    df = load_raw_dataset(sample_size=20000)
    df = preprocess_dataset(df)
    convs = reconstruct_conversations(df)
    brand, stats = analyze_and_select_brand(convs)
    print("Selected:", brand, stats)
