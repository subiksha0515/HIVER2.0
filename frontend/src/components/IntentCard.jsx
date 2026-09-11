import React from 'react';

export default function IntentCard({ intent, confidence }) {
  if (!intent) return null;

  const confPercent = Math.round((confidence || 0) * 100);

  // Intent color mapping
  const isUnknown = intent === 'OTHER / UNKNOWN';
  
  return (
    <div className="glass-card">
      <div className="card-title">
        <span>🎯</span>
        <span>Predicted Intent</span>
      </div>

      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', marginBottom: 6 }}>
        <div className="intent-badge" style={{ borderColor: isUnknown ? '#f43f5e' : 'rgba(99, 102, 241, 0.4)' }}>
          {intent}
        </div>
        <div style={{ fontFamily: 'var(--font-mono)', fontSize: '1.1rem', fontWeight: '700', color: confPercent >= 70 ? '#10b981' : confPercent >= 45 ? '#f59e0b' : '#f43f5e' }}>
          {confPercent}%
        </div>
      </div>

      <div className="conf-bar-track">
        <div 
          className="conf-bar-fill" 
          style={{ 
            width: `${confPercent}%`,
            background: confPercent >= 70 ? 'linear-gradient(90deg, #10b981, #06b6d4)' : confPercent >= 45 ? 'linear-gradient(90deg, #f59e0b, #6366f1)' : '#f43f5e'
          }} 
        />
      </div>

      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: 8 }}>
        <span>Confidence Calibrated Score</span>
        <span>Threshold: 45%</span>
      </div>
    </div>
  );
}
