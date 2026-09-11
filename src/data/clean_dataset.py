import re
import pandas as pd

def clean_tweet_text(text: str) -> str:
    """
    Lightly cleans tweet text while preserving natural customer language.
    Does NOT stem, lemmatize, or aggressively remove stopwords/emojis/punctuation.
    """
    if not isinstance(text, str):
        return ""
    # Remove null bytes or non-printable control characters (except standard whitespace)
    cleaned = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', text)
    # Standardize multi-spaces
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned

def preprocess_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """
    Preprocesses the raw dataframe:
    - Drops exact duplicate rows
    - Cleans tweet text
    - Removes empty text tweets
    - Formats timestamp
    """
    print(f"[clean_dataset] Starting preprocessing on {len(df):,} rows...")
    initial_count = len(df)
    
    # Drop exact duplicate rows
    df = df.drop_duplicates().copy()
    print(f"[clean_dataset] Dropped {initial_count - len(df):,} exact duplicate rows.")
    
    # Drop records with null tweet_id or author_id
    df = df.dropna(subset=['tweet_id', 'author_id']).copy()
    
    # Apply text cleaning
    df['cleaned_text'] = df['text'].astype(str).apply(clean_tweet_text)
    
    # Filter empty cleaned text
    empty_mask = df['cleaned_text'] == ""
    if empty_mask.sum() > 0:
        print(f"[clean_dataset] Dropping {empty_mask.sum():,} records with empty text.")
        df = df[~empty_mask].copy()
        
    print(f"[clean_dataset] Preprocessing complete. Remaining rows: {len(df):,}")
    return df

if __name__ == "__main__":
    from load_data import load_raw_dataset
    raw_df = load_raw_dataset(sample_size=1000)
    cleaned_df = preprocess_dataset(raw_df)
    print(cleaned_df[['tweet_id', 'author_id', 'cleaned_text']].head())
