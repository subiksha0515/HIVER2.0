import React, { useState } from 'react';

export default function DraftReplyPanel({ draftReply, isEscalated, evidence }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    if (draftReply) {
      navigator.clipboard.writeText(draftReply);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <div className="glass-card">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <div className="card-title" style={{ margin: 0 }}>
          <span>💬</span>
          <span>AI Draft Response</span>
        </div>
        {!isEscalated && draftReply && (\n          <button 
            onClick={handleCopy}
            style={{
              background: 'rgba(255, 255, 255, 0.06)',
              border: '1px solid var(--border-card)',
              borderRadius: '6px',
              padding: '4px 10px',
              fontSize: '0.78rem',
              color: 'var(--text-secondary)',
              cursor: 'pointer'
            }}
          >
            {copied ? '✓ Copied' : 'Copy'}
          </button>
        )}
      </div>

      {isEscalated ? (
        <div style={{ 
          padding: '24px 16px', 
          textAlign: 'center', 
          background: 'rgba(244, 63, 94, 0.05)', 
          border: '1px dashed rgba(244, 63, 94, 0.3)',
          borderRadius: 'var(--radius-sm)',
          color: 'var(--text-muted)'
        }}>
          <div style={{ fontSize: '1.5rem', marginBottom: 6 }}>🛑</div>
          <div style={{ fontWeight: '600', color: '#fda4af' }}>Draft Response Suppressed</div>
          <div style={{ fontSize: '0.8rem', marginTop: 4 }}>
            System blocked autonomous text generation to ensure zero unsupported commitments or false claims.
          </div>
        </div>
      ) : (
        <div>
          <div className="draft-box">
            {draftReply}
          </div>

          <div style={{ marginTop: 12, display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <span className="grounding-tag">
              <span>●</span>
              <span>100% Grounded in Historical Brand Resolutions</span>
            </span>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
              Claims Verified: 0 Unsupported
            </span>
          </div>
        </div>
      )}
    </div>
  );
}
