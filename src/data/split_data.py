import json
import random
import pandas as pd
from pathlib import Path
from typing import List, Dict, Any, Tuple

def create_leakage_safe_splits(
    conversations: List[Dict[str, Any]], 
    train_ratio: float = 0.70, 
    val_ratio: float = 0.15, 
    test_ratio: float = 0.15,
    seed: int = 42,
    output_dir: str = "data/processed"
) -> Dict[str, Any]:
    """
    Creates leakage-safe Train, Validation, and Test splits by conversation_id.
    Also creates a Temporal Test split based on conversation timestamp.
    """
    print(f"[split_data] Creating leakage-safe splits for {len(conversations):,} conversations...")
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Shuffle with fixed seed for random split reproducibility
    rng = random.Random(seed)
    shuffled_convs = list(conversations)
    rng.shuffle(shuffled_convs)
    
    total = len(shuffled_convs)
    train_end = int(total * train_ratio)
    val_end = train_end + int(total * val_ratio)
    
    train_convs = shuffled_convs[:train_end]
    val_convs = shuffled_convs[train_end:val_end]
    test_convs = shuffled_convs[val_end:]
    
    # Verification of zero leakage
    train_ids = set(c['conversation_id'] for c in train_convs)
    val_ids = set(c['conversation_id'] for c in val_convs)
    test_ids = set(c['conversation_id'] for c in test_convs)
    
    assert train_ids.isdisjoint(val_ids), "LEAKAGE ERROR: Overlap between Train and Val!"
    assert train_ids.isdisjoint(test_ids), "LEAKAGE ERROR: Overlap between Train and Test!"
    assert val_ids.isdisjoint(test_ids), "LEAKAGE ERROR: Overlap between Val and Test!"
    
    print(f"[split_data] Verified zero conversation ID overlap across splits.")
    
    # Temporal Evaluation Split (Latest 15% historically)
    try:
        sorted_convs = sorted(
            conversations, 
            key=lambda c: pd.to_datetime(c['timestamp'], format='%a %b %d %H:%M:%S %z %Y', errors='coerce')
        )
        temporal_test_start = int(total * (1.0 - test_ratio))
        temporal_test_convs = sorted_convs[temporal_test_start:]
    except Exception as e:
        print(f"[split_data] Warning: Temporal sorting error ({e}), fallback to test_convs.")
        temporal_test_convs = test_convs

    # Save to disk
    def save_jsonl(records: List[Dict[str, Any]], filename: str):
        path = Path(output_dir) / filename
        with open(path, "w", encoding="utf-8") as f:
            for r in records:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
        print(f"[split_data] Saved {len(records):,} records to {path}")

    save_jsonl(train_convs, "train.jsonl")
    save_jsonl(val_convs, "val.jsonl")
    save_jsonl(test_convs, "test.jsonl")
    save_jsonl(temporal_test_convs, "temporal_test.jsonl")
    
    split_summary = {
        "train_size": len(train_convs),
        "val_size": len(val_convs),
        "test_size": len(test_convs),
        "temporal_test_size": len(temporal_test_convs),
        "leakage_check_passed": True
    }
    return split_summary

if __name__ == "__main__":
    from load_data import load_raw_dataset
    from clean_dataset import preprocess_dataset
    from conversations import reconstruct_conversations
    from brand_selection import analyze_and_select_brand
    from discover_intents import extract_selected_brand_conversations, discover_and_assign_intents
    
    df = load_raw_dataset(sample_size=10000)
    df = preprocess_dataset(df)
    convs = reconstruct_conversations(df)
    brand, _ = analyze_and_select_brand(convs)
    brand_convs = extract_selected_brand_conversations(convs, brand)
    brand_convs, _ = discover_and_assign_intents(brand_convs)
    summary = create_leakage_safe_splits(brand_convs)
    print("Split summary:", summary)
