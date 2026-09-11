import os
import json
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Any

def analyze_raw_dataframe(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Performs comprehensive statistical and quality analysis of the raw Twitter dataset.
    """
    total_rows = len(df)
    columns = list(df.columns)
    dtypes = {col: str(df[col].dtype) for col in df.columns}
    missing_values = {col: int(df[col].isnull().sum()) for col in df.columns}
    missing_pct = {col: round(float(df[col].isnull().mean()) * 100, 2) for col in df.columns}
    
    # Duplicates check (exact row duplicates vs duplicate tweet_id)
    exact_duplicates = int(df.duplicated().sum())
    duplicate_tweet_ids = int(df['tweet_id'].duplicated().sum())
    
    # Inbound (customer) vs Outbound (brand)
    inbound_counts = df['inbound'].value_counts().to_dict()
    customer_tweets = int(inbound_counts.get(True, 0))
    brand_tweets = int(inbound_counts.get(False, 0))
    
    # Brands extraction (author_id for outbound tweets usually starts with brand name, or non-numeric author_ids)
    outbound_authors = df[df['inbound'] == False]['author_id'].value_counts()
    top_brands = outbound_authors.head(20).to_dict()
    total_unique_authors = int(df['author_id'].nunique())
    total_brands = int(outbound_authors.nunique())
    
    # Text length stats
    df['text_str'] = df['text'].fillna('')
    df['text_len'] = df['text_str'].str.len()
    text_len_stats = {
        'min': int(df['text_len'].min()),
        'max': int(df['text_len'].max()),
        'mean': round(float(df['text_len'].mean()), 2),
        'median': float(df['text_len'].median()),
        'short_under_10_chars': int((df['text_len'] < 10).sum()),
        'long_over_280_chars': int((df['text_len'] > 280).sum())
    }
    
    # Timestamp parsing
    try:
        timestamps = pd.to_datetime(df['created_at'], format='%a %b %d %H:%M:%S %z %Y', errors='coerce')
        min_date = str(timestamps.min())
        max_date = str(timestamps.max())
    except Exception:
        min_date = "Unknown"
        max_date = "Unknown"
        
    # Thread links
    has_in_reply = int(df['in_response_to_tweet_id'].notnull().sum())
    has_response = int(df['response_tweet_id'].notnull().sum())
    
    results = {
        'total_rows': total_rows,
        'columns': columns,
        'dtypes': dtypes,
        'missing_values': missing_values,
        'missing_pct': missing_pct,
        'exact_duplicates': exact_duplicates,
        'duplicate_tweet_ids': duplicate_tweet_ids,
        'customer_tweets': customer_tweets,
        'brand_tweets': brand_tweets,
        'total_unique_authors': total_unique_authors,
        'total_brands': total_brands,
        'top_brands': top_brands,
        'text_len_stats': text_len_stats,
        'date_range': {'min': min_date, 'max': max_date},
        'reply_links': {
            'has_in_reply_to_tweet_id': has_in_reply,
            'has_response_tweet_id': has_response
        }
    }
    return results

def generate_analysis_report(stats: Dict[str, Any], output_path: str = "reports/analysis_report.md") -> None:
    """
    Generates markdown report for dataset analysis.
    """
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    
    report_content = f"""# Dataset Analysis Report - Kaggle Twitter Customer Support

## 1. Overview Statistics
- **Total Rows**: {stats['total_rows']:,}
- **Total Columns**: {len(stats['columns'])}
- **Date Range**: {stats['date_range']['min']} to {stats['date_range']['max']}
- **Customer Tweets (Inbound)**: {stats['customer_tweets']:,} ({round(stats['customer_tweets']/stats['total_rows']*100, 2)}%)
- **Brand Tweets (Outbound)**: {stats['brand_tweets']:,} ({round(stats['brand_tweets']/stats['total_rows']*100, 2)}%)
- **Unique Authors**: {stats['total_unique_authors']:,}
- **Unique Brands**: {stats['total_brands']:,}

## 2. Column Specifications & Missing Values
| Column Name | Data Type | Missing Count | Missing % |
|---|---|---|---|
"""
    for col in stats['columns']:
        report_content += f"| `{col}` | `{stats['dtypes'][col]}` | {stats['missing_values'][col]:,} | {stats['missing_pct'][col]}% |\n"
        
    report_content += f"""
## 3. Data Quality Assessment
- **Exact Duplicate Rows**: {stats['exact_duplicates']:,}
- **Duplicate Tweet IDs**: {stats['duplicate_tweet_ids']:,}
- **Tweets with `in_response_to_tweet_id`**: {stats['reply_links']['has_in_reply_to_tweet_id']:,}
- **Tweets with `response_tweet_id`**: {stats['reply_links']['has_response_tweet_id']:,}
- **Extremely Short Messages (< 10 chars)**: {stats['text_len_stats']['short_under_10_chars']:,}
- **Long Messages (> 280 chars)**: {stats['text_len_stats']['long_over_280_chars']:,}
- **Mean Text Length**: {stats['text_len_stats']['mean']} characters (Median: {stats['text_len_stats']['median']})

## 4. Top 15 Brands by Volume
| Rank | Brand handle (`author_id`) | Total Brand Tweets |
|---|---|---|
"""
    top_items = list(stats['top_brands'].items())[:15]
    for idx, (brand, count) in enumerate(top_items, 1):
        report_content += f"| {idx} | `{brand}` | {count:,} |\n"
        
    report_content += """
## 5. Key Quality Insights & Pipeline Decisions
1. **Preservation of Customer Natural Language**: No aggressive text stemming or stopword removal will be performed on raw tweets to preserve semantic intent and tone.
2. **Missing In-Reply Links**: A subset of inbound tweets lack `in_response_to_tweet_id` (starting new threads), while outbound brand tweets heavily use `in_response_to_tweet_id` linking back to customer queries.
3. **Multi-Response Complications**: Some brand replies link multiple response tweet IDs separated by commas. Graph reconstruction handles comma-separated lists to reconstruct complete conversation trees.
"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report_content)
    print(f"[analyze_dataset] Report generated at {output_path}")

if __name__ == "__main__":
    from load_data import load_raw_dataset
    df = load_raw_dataset(sample_size=5000)
    stats = analyze_raw_dataframe(df)
    generate_analysis_report(stats)
