import React from 'react';

export default function EvidencePanel({ cases }) {
  if (!cases || cases.length === 0) return null;

  return (
    <div className="glass-card">
      <div className="card-title">
        <span>📚</span>
        <span>Historical Evidence (Grounding Cases)</span>
      </div>

      <div className="evidence-list">
        {cases.slice(0, 3).map((item, idx) => {
          const simScore = Math.round((item.similarity_score || 0) * 100);
          return (
            <div key={item.conversation_id || idx} className="evidence-card">
              <div className="evidence-header">
                <span>Rank #{item.rank || idx + 1} • {item.conversation_id}</span>
                <span className="similarity-tag">{simScore}% Similarity</span>
              </div>

              <div className="evidence-customer">
                <strong style={{ color: '#cbd5e1' }}>User: </strong>
                "{item.customer_message}"
              </div>

              <div className="evidence-brand">
                <strong style={{ color: '#818cf8' }}>Resolution: </strong>
                {item.brand_response}
              </div>

              <div style={{ marginTop: 8, fontSize: '0.72rem', color: 'var(--text-muted)' }}>
                Intent: <span style={{ color: '#94a3b8' }}>{item.intent}</span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
