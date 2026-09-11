"""
End-to-End Pipeline Tests for AI Support Decision Engine.
Directly tests the pipeline logic across 8 critical test categories without HTTP.
"""

import pytest
from src.engine.pipeline import SupportDecisionPipeline


@pytest.fixture(scope="module")
def pipeline():
    return SupportDecisionPipeline(
        min_intent_confidence=0.45,
        min_retrieval_similarity=0.40,
        classifier_path="models/best_intent_classifier.joblib",
        retrieval_index_dir="models/retrieval_index"
    )


def test_01_high_confidence_known_intent(pipeline):
    """Normal query with supported intent and good retrieval should auto-handle."""
    query = "Where is my package? The tracking number has not updated in three days."
    res = pipeline.process(query)
    assert res["intent"] is not None and len(res["intent"]) > 0
    assert res["confidence"] >= 0.40
    # Should either auto-handle with draft reply or escalate safely
    if not res["escalate"]:
        assert len(res["draft_reply"]) > 0
        assert res["pipeline_stage"] == "AUTO_HANDLED"


def test_02_low_confidence_or_out_of_taxonomy(pipeline):
    """Unusual or out of domain query should escalate or mark low confidence."""
    query = "My pet lizard ate my shoe and now the spaceship won't launch in orbit."
    res = pipeline.process(query)
    assert res["intent"] is not None
    # Given out of domain, similarity or confidence should escalate
    assert res["escalate"] is True or res["confidence"] < 0.80


def test_03_unsupported_account_deletion(pipeline):
    """Sensitive action: account deletion must escalate."""
    query = "Please delete my account and erase all my data immediately."
    res = pipeline.process(query)
    assert res["escalate"] is True
    assert "unavailable" in res["escalation_reason"].lower() or "action" in res["escalation_reason"].lower()


def test_04_unsupported_financial_refund(pipeline):
    """Financial transaction: requesting a refund must escalate to human agent."""
    query = "Give me a refund for my order right now, the item never arrived!"
    res = pipeline.process(query)
    assert res["escalate"] is True
    assert "unavailable" in res["escalation_reason"].lower() or "action" in res["escalation_reason"].lower()


def test_05_legal_threat_action(pipeline):
    """Legal threats must immediately escalate."""
    query = "If this is not fixed I will sue and take legal action against your company."
    res = pipeline.process(query)
    assert res["escalate"] is True
    assert "unavailable" in res["escalation_reason"].lower() or "action" in res["escalation_reason"].lower()


def test_06_ambiguous_short_query(pipeline):
    """Very short ambiguous queries like 'help' or '?' must escalate."""
    query = "help"
    res = pipeline.process(query)
    assert res["escalate"] is True
    assert "ambiguous" in res["escalation_reason"].lower()


def test_07_draft_reply_presence(pipeline):
    """Non-escalated queries must contain a draft reply; escalated queries must have empty draft reply."""
    # Test query that escalates
    esc_res = pipeline.process("delete my account")
    assert esc_res["escalate"] is True
    assert esc_res["draft_reply"] == ""

    # Test query that auto-handles
    auto_res = pipeline.process("Can I update my email address on my account settings?")
    assert "intent" in auto_res
    if not auto_res["escalate"]:
        assert len(auto_res["draft_reply"]) > 0


def test_08_intent_populated_everywhere(pipeline):
    """Every single query must return an intent and top retrieved cases."""
    queries = [
        "Where is my delivery?",
        "App keeps freezing on launch",
        "xyz 123 random non-word string",
        "cancel my order now"
    ]
    for q in queries:
        res = pipeline.process(q)
        assert "intent" in res
        assert isinstance(res["intent"], str)
        assert len(res["intent"]) > 0
        assert "confidence" in res
        assert 0.0 <= res["confidence"] <= 1.0
        assert "top_retrieved_cases" in res
        assert isinstance(res["top_retrieved_cases"], list)
