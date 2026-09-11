import urllib.request
import json

def test_query(msg):
    req = urllib.request.Request(
        "http://localhost:5173/api/support",
        data=json.dumps({"message": msg}).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as r:
        res = json.loads(r.read().decode())
        print(f"\nQuery: '{msg}'")
        print(f"  Decision: {res['decision']}")
        print(f"  Intent: {res['intent']} (conf={res['intent_confidence']})")
        if res.get('escalation_reason'):
            print(f"  Escalation Reason: {res['escalation_reason']}")
        if res.get('draft_reply'):
            print(f"  Draft Reply: {res['draft_reply'][:100]}...")
        print("  Trust Checks Passed:", sum(1 for c in res.get('trust_checks', []) if c['passed']), "/", len(res.get('trust_checks', [])))

if __name__ == "__main__":
    test_query("Where is my package? My delivery tracking is delayed.")
    test_query("I was charged twice for Prime, give me a refund now!")
    test_query("Please delete my account immediately.")
    test_query("help")
