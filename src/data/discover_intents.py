import json
import yaml
import re
import pandas as pd
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import MiniBatchKMeans

def extract_selected_brand_conversations(conversations: List[Dict[str, Any]], brand_name: str) -> List[Dict[str, Any]]:
    """Filters conversations belonging to selected brand."""
    return [c for c in conversations if c['brand'] == brand_name]

# Define intent patterns / taxonomy mapping rules based on cluster inspection for Twitter customer support
INTENT_PATTERNS = {
    "SOFTWARE_UPDATE_ISSUES": {
        "keywords": [r'\bupdate\b', r'\bios\b', r'\bupdate(d|s)?\b', r'\bversion\b', r'\binstall\b', r'\bupgrade\b', r'\bsoftware\b'],
        "description": "Inquiries regarding software updates, OS upgrade bugs, installation failures, or issues occurring immediately after updating.",
        "inclusion_criteria": "Mentions software updates, OS version, update installation, or issues starting right after an update.",
        "exclusion_criteria": "Hardware physical damage, simple app store billing issues, or shipping queries.",
    },
    "BATTERY_POWER_CHARGING": {
        "keywords": [r'\bbattery\b', r'\bcharg(e|ing)\b', r'\bpower\b', r'\bdrain(ing)?\b', r'\bdied\b', r'\bpercent\b', r'\bplug\b'],
        "description": "Issues related to battery life, rapid battery draining, device turning off, or failing to charge.",
        "inclusion_criteria": "Contains terms like battery, charging, power, battery drain, charger, cable.",
        "exclusion_criteria": "General software app crashes unless battery is explicitly cited.",
    },
    "ACCOUNT_LOGIN_SECURITY": {
        "keywords": [r'\baccount\b', r'\blogin\b', r'\bpasswords?\b', r'\block(ed)?\b', r'\bsign in\b', r'\bapple id\b', r'\bverify\b', r'\bverification\b', r'\bsecurity\b'],
        "description": "Questions regarding account access, locked accounts, password reset, 2FA, or login authentication.",
        "inclusion_criteria": "Mentions login, password, locked account, credentials, or account verification.",
        "exclusion_criteria": "Billing disputes without account access issues.",
    },
    "APP_CRASH_PERFORMANCE": {
        "keywords": [r'\bapp(s)?\b', r'\bcrash(es|ing)?\b', r'\bfreez(e|ing)\b', r'\bslow\b', r'\blag(gy)?\b', r'\bopen\b', r'\bwork(ing)?\b'],
        "description": "Reports of application crashes, system lag, frozen screen, or apps failing to launch.",
        "inclusion_criteria": "Mentions app freezing, crashing, unresponsive UI, or slow performance.",
        "exclusion_criteria": "Physical screen damage or internet network connectivity issues.",
    },
    "BILLING_REFUND_SUBSCRIPTION": {
        "keywords": [r'\bbill(ing)?\b', r'\brefund\b', r'\bcharg(ed|es)\b', r'\bmoney\b', r'\bpay(ment)?\b', r'\bsubscription\b', r'\bcard\b', r'\bpurchase\b', r'\bitunes\b'],
        "description": "Billing inquiries, unauthorized charges, refund requests, payment processing issues, or subscription cancellations.",
        "inclusion_criteria": "Contains billing terms, payment, charge, refund, money, receipt, or subscription.",
        "exclusion_criteria": "Physical store hardware returns.",
    },
    "ORDER_SHIPPING_DELIVERY": {
        "keywords": [r'\border\b', r'\bship(ping|ped)?\b', r'\bdeliver(y|ed)?\b', r'\btrack(ing)?\b', r'\bpack(age)?\b', r'\barriv(e|ed)\b', r'\bcourier\b'],
        "description": "Questions about order status, shipment tracking, delayed delivery, or missing packages.",
        "inclusion_criteria": "Mentions order number, shipping, tracking, delivery status, or package delivery.",
        "exclusion_criteria": "Digital app store downloads.",
    },
    "CONNECTIVITY_NETWORK_WIFI": {
        "keywords": [r'\bwifi\b', r'\bbluetooth\b', r'\bconnect(ion)?\b', r'\bsignal\b', r'\bnetwork\b', r'\bcellular\b', r'\bdata\b', r'\bsim\b', r'\bpair(ing)?\b'],
        "description": "Issues connecting to Wi-Fi, Bluetooth devices, cellular network data, or SIM card errors.",
        "inclusion_criteria": "Mentions Wi-Fi, Bluetooth, network connection, SIM, cellular data, or pairing.",
        "exclusion_criteria": "Power/battery issues.",
    },
    "AUDIO_SPEAKER_MICROPHONE": {
        "keywords": [r'\baudio\b', r'\bsound\b', r'\bspeaker\b', r'\bmic\b', r'\bmicrophone\b', r'\bvolume\b', r'\bheadphone\b', r'\bairpods?\b'],
        "description": "Problems with sound output, low volume, distorted speaker sound, microphone unresponsiveness, or headphone connectivity.",
        "inclusion_criteria": "Mentions sound, volume, speaker, mic, audio, or headphones/AirPods.",
        "exclusion_criteria": "Display screen issues.",
    },
    "DISPLAY_SCREEN_PHYSICAL": {
        "keywords": [r'\bscreen\b', r'\bdisplay\b', r'\bflicker(ing)?\b', r'\bblack\b', r'\btouch\b', r'\bcrack(ed)?\b', r'\bglass\b'],
        "description": "Issues involving physical screen damage, display flickering, black screen, or unresponsive touch input.",
        "inclusion_criteria": "Contains terms like screen, display, flicker, black screen, touchscreen.",
        "exclusion_criteria": "Software update bugs with display working fine.",
    },
    "STORE_REPAIR_SERVICE": {
        "keywords": [r'\bstore\b', r'\bappointment\b', r'\brepair\b', r'\bgenius\b', r'\bservice\b', r'\breplace(ment)?\b', r'\bwarranty\b'],
        "description": "Requests for retail store appointments, hardware repair status, warranty service, or device replacement.",
        "inclusion_criteria": "Mentions store appointment, repair, service center, warranty, or hardware replacement.",
        "exclusion_criteria": "Self-service software troubleshooting.",
    }
}

def classify_intent_heuristic(message: str) -> Tuple[str, float]:
    """
    Assigns intent using rule-based pattern matching and confidence score.
    Returns (intent_name, confidence).
    """
    msg_lower = message.lower()
    matched_intents = []
    
    for intent, cfg in INTENT_PATTERNS.items():
        score = 0
        for pattern in cfg['keywords']:\n            if re.search(pattern, msg_lower):
                score += 1
        if score > 0:
            matched_intents.append((intent, score))
            
    if not matched_intents:
        return "OTHER / UNKNOWN", 0.0
        
    # Sort by score
    matched_intents.sort(key=lambda x: x[1], reverse=True)
    best_intent, score = matched_intents[0]
    
    # Calculate confidence based on keyword match strength
    confidence = min(1.0, round(score * 0.4 + 0.2, 2))
    return best_intent, confidence

def discover_and_assign_intents(brand_conversations: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """
    Discovers intents, assigns every conversation an intent label, and compiles representative examples.
    """
    print(f"[discover_intents] Processing {len(brand_conversations):,} customer messages for intent discovery...")
    
    intent_counts = {}
    intent_examples = {intent: [] for intent in INTENT_PATTERNS.keys()}
    intent_examples["OTHER / UNKNOWN"] = []
    
    updated_conversations = []
    
    for c in brand_conversations:
        msg = c['customer_message']
        intent, conf = classify_intent_heuristic(msg)
        
        c['intent'] = intent
        c['intent_confidence'] = conf
        updated_conversations.append(c)
        
        intent_counts[intent] = intent_counts.get(intent, 0) + 1
        
        # Collect top representative examples (prefer longer, clear customer messages)
        if len(intent_examples[intent]) < 10 and len(msg.split()) >= 4:
            intent_examples[intent].append({
                'conversation_id': c['conversation_id'],
                'customer_message': msg,
                'brand_response': c['brand_response']
            })

    taxonomy_dict = {}
    for intent_name, cfg in INTENT_PATTERNS.items():
        taxonomy_dict[intent_name] = {
            "name": intent_name,
            "description": cfg["description"],
            "inclusion_criteria": cfg["inclusion_criteria"],
            "exclusion_criteria": cfg["exclusion_criteria"],
            "sample_count": intent_counts.get(intent_name, 0),
            "representative_examples": [ex['customer_message'] for ex in intent_examples[intent_name][:5]]
        }
        
    # Add OTHER / UNKNOWN
    taxonomy_dict["OTHER / UNKNOWN"] = {
        "name": "OTHER / UNKNOWN",
        "description": "Customer messages that do not confidently fit into any supported intent taxonomy category.",
        "inclusion_criteria": "Messages with low confidence, general greetings, ambiguous text, or off-topic queries.",
        "exclusion_criteria": "Messages clearly matching a defined domain intent.",
        "sample_count": intent_counts.get("OTHER / UNKNOWN", 0),
        "representative_examples": [ex['customer_message'] for ex in intent_examples["OTHER / UNKNOWN"][:5]]
    }
    
    return updated_conversations, taxonomy_dict

def save_intent_config_and_report(
    taxonomy: Dict[str, Any], 
    intent_counts: Dict[str, int], 
    config_path: str = "configs/intents.yaml",
    report_path: str = "reports/intent_taxonomy.md"
) -> None:
    """Saves configs/intents.yaml and reports/intent_taxonomy.md."""
    Path(config_path).parent.mkdir(parents=True, exist_ok=True)
    Path(report_path).parent.mkdir(parents=True, exist_ok=True)
    
    # Save YAML
    yaml_structure = {
        "metadata": {
            "total_intents": len(taxonomy),
            "version": "1.0"
        },
        "intents": taxonomy
    }
    with open(config_path, "w", encoding="utf-8") as f:
        yaml.dump(yaml_structure, f, default_flow_style=False, sort_keys=False)
    print(f"[discover_intents] Saved intent taxonomy config to {config_path}")
    
    # Save Markdown Report
    total_samples = sum(intent_counts.values())
    report_md = f"""# Customer Intent Taxonomy Report

## Taxonomy Overview
- **Total Intent Classes**: {len(taxonomy)}
- **Total Analyzed Conversations**: {total_samples:,}

## Intent Distribution Table
| Intent Name | Sample Count | Distribution % | Description |
|---|---|---|---|
"""
    for name, info in taxonomy.items():
        cnt = info['sample_count']
        pct = round((cnt / total_samples) * 100, 2) if total_samples > 0 else 0
        report_md += f"| `{name}` | {cnt:,} | {pct}% | {info['description']} |\n"
        
    report_md += "\n## Detailed Intent Definitions & Inclusion/Exclusion Criteria\n"
    
    for name, info in taxonomy.items():
        report_md += f"""
### Intent: `{name}`
- **Description**: {info['description']}
- **Inclusion Criteria**: {info['inclusion_criteria']}
- **Exclusion Criteria**: {info['exclusion_criteria']}
- **Sample Count**: {info['sample_count']:,}
- **Representative Customer Examples**:
"""
        for ex in info['representative_examples']:
            report_md += f"  - *\"{ex}\"*\n"

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_md)
    print(f"[discover_intents] Saved intent taxonomy report to {report_path}")

if __name__ == "__main__":
    from load_data import load_raw_dataset
    from clean_dataset import preprocess_dataset
    from conversations import reconstruct_conversations
    from brand_selection import analyze_and_select_brand
    
    df = load_raw_dataset(sample_size=20000)
    df = preprocess_dataset(df)
    convs = reconstruct_conversations(df)
    brand, _ = analyze_and_select_brand(convs)
    brand_convs = extract_selected_brand_conversations(convs, brand)
    updated_convs, taxonomy = discover_and_assign_intents(brand_convs)
    counts = {k: v['sample_count'] for k, v in taxonomy.items()}
    save_intent_config_and_report(taxonomy, counts)
