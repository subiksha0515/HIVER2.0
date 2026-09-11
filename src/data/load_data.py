import os
import glob
import pandas as pd
from pathlib import Path

DATASET_HANDLE = "thoughtvector/customer-support-on-twitter"
RAW_DATA_DIR = Path("data/raw")

def get_dataset_path() -> Path:
    """
    Locates or downloads the Twitter Customer Support dataset (twcs.csv).
    Returns path to twcs.csv.
    """
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
    target_path = RAW_DATA_DIR / "twcs.csv"
    
    if target_path.exists() and target_path.stat().st_size > 0:
        print(f"[load_data] Found existing raw dataset at: {target_path}")
        return target_path

    # Check if downloaded in kagglehub cache or download via kagglehub
    print(f"[load_data] Downloading dataset '{DATASET_HANDLE}' via kagglehub...")
    try:
        import kagglehub
        downloaded_path = kagglehub.dataset_download(DATASET_HANDLE)
        print(f"[load_data] Downloaded to cache: {downloaded_path}")
        
        # Search specifically for twcs.csv first (full dataset)
        twcs_files = glob.glob(os.path.join(downloaded_path, "**", "twcs.csv"), recursive=True)
        if twcs_files:
            source_csv = Path(twcs_files[0])
            print(f"[load_data] Found full dataset twcs.csv at: {source_csv}")
            return source_csv
            
        csv_files = glob.glob(os.path.join(downloaded_path, "*.csv"))
        if not csv_files:
            csv_files = glob.glob(os.path.join(downloaded_path, "**", "*.csv"), recursive=True)
            
        if csv_files:
            # Sort to avoid sample.csv
            csv_files.sort(key=lambda x: os.path.getsize(x), reverse=True)
            source_csv = Path(csv_files[0])
            print(f"[load_data] Found dataset file: {source_csv}")
            return source_csv
        else:
            raise FileNotFoundError(f"No CSV files found in kagglehub output: {downloaded_path}")
    except Exception as e:
        print(f"[load_data] Error fetching dataset via kagglehub: {e}")
        raise RuntimeError(f"Could not acquire dataset {DATASET_HANDLE}. Error: {e}")

def load_raw_dataset(sample_size: int = None) -> pd.DataFrame:
    """
    Loads raw twcs.csv into pandas DataFrame.
    """
    csv_path = get_dataset_path()
    print(f"[load_data] Loading raw dataset from {csv_path}...")
    
    # Load dataset
    dtype_spec = {
        'tweet_id': 'str',
        'author_id': 'str',
        'inbound': 'bool',
        'created_at': 'str',
        'text': 'str',
        'response_tweet_id': 'str',
        'in_response_to_tweet_id': 'str'
    }
    
    if sample_size:
        df = pd.read_csv(csv_path, nrows=sample_size, dtype=dtype_spec)
    else:
        df = pd.read_csv(csv_path, dtype=dtype_spec)
        
    print(f"[load_data] Loaded {len(df):,} rows and {len(df.columns)} columns.")
    return df

if __name__ == "__main__":
    df = load_raw_dataset(sample_size=1000)
    print("Columns:", list(df.columns))
    print("Head:\n", df.head(3))
