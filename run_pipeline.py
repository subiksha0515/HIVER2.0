import os
import sys
import json
import time
from pathlib import Path

# Add src/ to sys.path
sys.path.insert(0, str(Path(__file__).parent / "src" / "data"))

from load_data import load_raw_dataset
from analyze_dataset import analyze_raw_dataframe, generate_analysis_report
from clean_dataset import preprocess_dataset
from conversations import reconstruct_conversations, save_conversations
from brand_selection import analyze_and_select_brand
from discover_intents import extract_selected_brand_conversations, discover_and_assign_intents, save_intent_config_and_report
from split_data import create_leakage_safe_splits

def run_phase1_pipeline():
    start_time = time.time()
    print("=" * 70)
    print("STARTING PHASE 1: DATA UNDERSTANDING & INTENT-DISCOVERY PIPELINE")
    print("=" * 70)

    # 1. Load Raw Dataset
    print("\n--- STEP 1 & 2: Loading & Inspecting Dataset ---")
    raw_df = load_raw_dataset()
    
    # 2. Dataset Quality & Statistical Inspection
    print("\n--- Generating Analysis Report ---")
    raw_stats = analyze_raw_dataframe(raw_df)
    generate_analysis_report(raw_stats, output_path="reports/analysis_report.md")

    # 3. Clean & Preprocess Dataset
    print("\n--- STEP 3: Preprocessing & Quality Cleaning ---")
    cleaned_df = preprocess_dataset(raw_df)

    # 4. Conversation Graph Reconstruction
    print("\n--- STEP 5: Reconstructing Multi-Turn Conversations ---")
    all_conversations = reconstruct_conversations(cleaned_df)
    save_conversations(all_conversations, "data/processed/conversations.jsonl")

    # 5. Data-Driven Brand Selection
    print("\n--- STEP 4: Selecting Brand ---")
    selected_brand, brand_stats = analyze_and_select_brand(all_conversations, output_report_path="reports/brand_selection.md")

    # 6. Intent Discovery on Selected Brand
    print("\n--- STEP 6: Discovering Customer Intents ---")
    brand_convs = extract_selected_brand_conversations(all_conversations, selected_brand)
    print(f"Total reconstructed conversations for '{selected_brand}': {len(brand_convs):,}")
    
    labeled_convs, intent_taxonomy = discover_and_assign_intents(brand_convs)
    intent_counts = {k: v['sample_count'] for k, v in intent_taxonomy.items()}
    save_intent_config_and_report(
        intent_taxonomy, 
        intent_counts, 
        config_path="configs/intents.yaml",
        report_path="reports/intent_taxonomy.md"
    )

    # 7. Leakage-Safe Data Splitting
    print("\n--- STEP 7: Creating Leakage-Safe Data Splits ---")
    split_summary = create_leakage_safe_splits(labeled_convs, output_dir="data/processed")

    # 8. Output Validation
    print("\n--- STEP 8: Validating Pipeline Artifacts ---")
    required_files = [
        "data/processed/conversations.jsonl",
        "data/processed/train.jsonl",
        "data/processed/val.jsonl",
        "data/processed/test.jsonl",
        "data/processed/temporal_test.jsonl",
        "configs/intents.yaml",
        "reports/analysis_report.md",
        "reports/brand_selection.md",
        "reports/intent_taxonomy.md"
    ]
    
    missing_files = []
    for f in required_files:
        p = Path(f)
        if not p.exists() or p.stat().st_size == 0:
            missing_files.append(f)
            
    if missing_files:
        print(f"ERROR: Missing or empty pipeline artifacts: {missing_files}")
        sys.exit(1)

    elapsed = round(time.time() - start_time, 2)
    print("\n" + "=" * 70)
    print(f"PHASE 1 PIPELINE COMPLETED SUCCESSFULLY IN {elapsed} SECONDS")
    print("=" * 70)
    
    # Print concise summary
    print("\n--- SUMMARY OF RESULTS ---")
    print(f"1. Selected Brand: {selected_brand}")
    print(f"2. Number of Usable Conversations ({selected_brand}): {len(brand_convs):,}")
    print(f"3. Final Intent Count: {len(intent_taxonomy)}")
    print(f"4. Intent Names: {list(intent_taxonomy.keys())}")
    print(f"5. Train / Val / Test Sizes: {split_summary['train_size']:,} / {split_summary['val_size']:,} / {split_summary['test_size']:,} (Temporal: {split_summary['temporal_test_size']:,})")
    print(f"6. Primary Quality Issues Addressed: Missing thread links, broken/null texts, comma-separated response IDs, and natural language preservation.")
    print(f"7. Pipeline Artifacts Created:")
    for f in required_files:
        print(f"   - {f}")
    print("8. Unresolved Problems: None.")

if __name__ == "__main__":
    run_phase1_pipeline()
