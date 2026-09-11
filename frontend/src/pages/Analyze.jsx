import React, { useState } from 'react';
import IntentCard from '../components/IntentCard';
import EvidencePanel from '../components/EvidencePanel';
import DecisionPanel from '../components/DecisionPanel';
import TrustExplainer from '../components/TrustExplainer';
import DraftReplyPanel from '../components/DraftReplyPanel';

const SAMPLE_QUERIES = [
  {
    label: '📦 Tracking Delay',
    text: 'Where is my package? My delivery tracking is delayed.'
  },
  {
    label: '💰 Refund Request (Escalate)',
    text: 'I was charged twice for my subscription, give me a refund right now!'
  },
  {
    label: '🗑️ Account Deletion (Escalate)',
    text: 'Please delete my account and remove my credit card immediately.'
  },
  {
    label: '📱 App Crashing',
    text: 'My Kindle app keeps crashing on launch whenever I open a new book.'
  },
  {
    label: '❓ Ambiguous (Escalate)',
    text: 'help'
  }
];

export default function Analyze() {
  const [message, setMessage] = useState(SAMPLE_QUERIES[0].text);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleAnalyze = async (msgToAnalyze) => {
    const text = typeof msgToAnalyze === 'string' ? msgToAnalyze : message;
    if (!text.trim()) return;

    setLoading(true);
    setError(null);

    try {
      const res = await fetch('/api/support', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text.trim() })
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.detail || `Server error (${res.status})`);
      }

      const data = await res.json();
      setResult(data);
    } catch (err) {
      console.error(err);
      setError(err.message || 'Failed to connect to AI Support API.');
    } finally {
      setLoading(false);
    }
  };

  const handleSelectSample = (sampleText) => {
    setMessage(sampleText);
    handleAnalyze(sampleText);
  };

  return (
    <div>
      {/* Input Form Card */}
      <div className="glass-card">
        <div className="input-header">
          <label htmlFor="customer-message" className="card-title" style={{ margin: 0 }}>
            <span>✉️</span>
            <span>Customer Message</span>
          </label>
          <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
            Natural Language Support Request
          </span>
        </div>

        <textarea
          id="customer-message"
          className="textarea-custom"
          rows={3}
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="Type or paste a customer query here..."
        />

        <div className="input-actions">
          <div className="samples-group">
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginRight: 4 }}>
              Presets:
            </span>
            {SAMPLE_QUERIES.map((s, idx) => (
              <button
                key={idx}
                type="button"
                className="sample-chip"
                onClick={() => handleSelectSample(s.text)}
              >
                {s.label}
              </button>
            ))}
          </div>

          <button
            id="btn-analyze"
            type="button"
            className="btn-primary"
            onClick={() => handleAnalyze()}
            disabled={loading || !message.trim()}
          >
            {loading ? (
              <>
                <span className="status-dot" style={{ background: '#ffffff', boxShadow: 'none' }} />
                <span>Analyzing...</span>
              </>
            ) : (
              <>
                <span>⚡</span>
                <span>Analyze Message</span>
              </>
            )}
          </button>
        </div>
      </div>

      {error && (
        <div style={{
          padding: '16px',
          borderRadius: 'var(--radius-sm)',
          background: 'var(--danger-bg)',
          border: '1px solid var(--danger-border)',
          color: '#fecdd3',
          marginBottom: '24px'
        }}>
          <strong>Analysis Failed:</strong> {error}
        </div>
      )}

      {/* Analysis Results Display */}
      {result && (
        <div>
          {/* Decision Banner */}
          <DecisionPanel
            decision={result.decision}
            reason={result.escalation_reason}
            stage={result.pipeline_stage}
          />

          <div className="results-grid">
            {/* Left Column: Intent, Draft Reply, Trust Explainer */}
            <div>
              <IntentCard
                intent={result.intent}
                confidence={result.intent_confidence}
              />

              <DraftReplyPanel
                draftReply={result.draft_reply}
                isEscalated={result.decision === 'ESCALATE'}
                evidence={result.evidence}
              />

              <TrustExplainer
                checks={result.trust_checks}
                decision={result.decision}
              />
            </div>

            {/* Right Column: Historical Evidence */}
            <div>
              <EvidencePanel cases={result.retrieved_cases} />
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
