import pandas as pd
import json
import re
from pathlib import Path
from typing import List, Dict, Any, Tuple

# Positive resolution indicators in customer reply
RESOLUTION_KEYWORDS = [
    r'\bthank(s|\s+you)?\b', r'\bfixed\b', r'\bsolved\b', r'\bworked\b', 
    r'\bgreat\b', r'\bawesome\b', r'\bperfect\b', r'\bhelpful\b', r'\bappreciate\b'
]

def check_resolution_available(history: List[Dict[str, Any]]) -> bool:
    """
    Evaluates reasonable evidence for whether the conversation reached a resolution.
    Returns True if:
    - Customer expresses gratitude or confirms resolution in multi-turn conversation.
    - Brand gave complete resolution and customer acknowledged.
    """
    if len(history) < 2:
        return False
        
    customer_messages = [msg['text'].lower() for msg in history if msg.get('inbound')]
    brand_messages = [msg['text'].lower() for msg in history if not msg.get('inbound')]
    
    if not customer_messages or not brand_messages:
        return False
        
    # Check latest customer messages for resolution keywords
    for msg in customer_messages[1:]:  # Replies after initial query
        for kw in RESOLUTION_KEYWORDS:
            if re.search(kw, msg):
                return True
                
    return False

def reconstruct_conversations(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Reconstructs multi-turn conversation trees from raw tweet rows.
    """
    print(f"[conversations] Indexing {len(df):,} tweets for graph reconstruction...")
    
    # Build tweet lookup index: tweet_id -> dict
    tweets = {}
    for row in df.itertuples(index=False):
        tweets[str(row.tweet_id)] = {
            'tweet_id': str(row.tweet_id),
            'author_id': str(row.author_id),
            'inbound': bool(row.inbound),
            'created_at': str(row.created_at),
            'text': str(getattr(row, 'cleaned_text', row.text)),
            'response_tweet_id': str(row.response_tweet_id) if pd.notnull(row.response_tweet_id) else None,
            'in_response_to_tweet_id': str(row.in_response_to_tweet_id) if pd.notnull(row.in_response_to_tweet_id) else None,
        }
        
    # Identify root customer tweets (inbound == True & no parent or parent not in tweets)
    root_tweet_ids = []
    for tid, t in tweets.items():
        if t['inbound']:
            parent = t['in_response_to_tweet_id']
            if not parent or parent not in tweets:
                root_tweet_ids.append(tid)
                
    print(f"[conversations] Identified {len(root_tweet_ids):,} root customer inquiries.")
    
    conversations = []
    visited_tweets = set()
    
    for idx, root_id in enumerate(root_tweet_ids):
        if root_id in visited_tweets:
            continue
            
        root = tweets[root_id]
        history = [root]
        visited_tweets.add(root_id)
        
        # Traverse downstream responses
        curr_ids = [root_id]
        brand_name = None
        
        while curr_ids:
            next_ids = []
            for cid in curr_ids:
                curr_t = tweets[cid]
                resp_str = curr_t['response_tweet_id']
                if resp_str:
                    # Can be comma separated
                    child_ids = [c.strip() for c in resp_str.split(',') if c.strip()]
                    for child_id in child_ids:
                        if child_id in tweets and child_id not in visited_tweets:
                            visited_tweets.add(child_id)
                            child_t = tweets[child_id]
                            history.append(child_t)
                            next_ids.append(child_id)
                            if not child_t['inbound'] and not brand_name:
                                brand_name = child_t['author_id']
            curr_ids = next_ids
            
        # Ensure we have at least one brand response in the thread
        brand_responses = [t['text'] for t in history if not t['inbound']]
        if not brand_responses:
            continue
            
        if not brand_name:
            # find first brand author
            for t in history:
                if not t['inbound']:
                    brand_name = t['author_id']
                    break
                    
        cust_first_msg = root['text']
        brand_first_resp = brand_responses[0]
        
        # Format history for structured record
        formatted_history = [
            {
                'tweet_id': t['tweet_id'],
                'author_id': t['author_id'],
                'inbound': t['inbound'],
                'created_at': t['created_at'],
                'text': t['text']
            }
            for t in history
        ]
        
        resolution = check_resolution_available(formatted_history)
        
        conv_record = {
            'conversation_id': f"conv_{root_id}",
            'root_tweet_id': root_id,
            'brand': brand_name or "UnknownBrand",
            'customer_id': root['author_id'],
            'timestamp': root['created_at'],
            'customer_message': cust_first_msg,
            'brand_response': brand_first_resp,
            'conversation_history': formatted_history,
            'turns': len(formatted_history),
            'resolution_available': resolution
        }
        conversations.append(conv_record)
        
    print(f"[conversations] Successfully reconstructed {len(conversations):,} complete conversations.")
    return conversations

def save_conversations(conversations: List[Dict[str, Any]], output_path: str = "data/processed/conversations.jsonl") -> None:
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        for c in conversations:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")
    print(f"[conversations] Saved reconstructed conversations to {output_path}")

if __name__ == "__main__":
    from load_data import load_raw_dataset
    from clean_dataset import preprocess_dataset
    
    df = load_raw_dataset(sample_size=10000)
    df = preprocess_dataset(df)
    convs = reconstruct_conversations(df)
    save_conversations(convs, "data/processed/sample_conversations.jsonl")
