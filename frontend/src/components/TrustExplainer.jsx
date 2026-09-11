import React from 'react';

export default function TrustExplainer({ checks, decision }) {
  if (!checks || checks.length === 0) return null;

  return (
    <div className="glass-card">
      <div className="card-title">
        <span>🛡️</span>
        <span>Trust & Safety Policy Explainer</span>
      </div>

      <div className="trust-checklist">
        {checks.map((c, idx) => (
          <div key={idx} className="trust-item">
            <span className={`trust-icon ${c.passed ? 'pass' : 'fail'}`}>
              {c.passed ? '✓' : '✕'}
            </span>
            <div style={{ flex: 1 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ fontWeight: '600', color: c.passed ? '#f8fafc' : '#f43f5e' }}>
                  {c.check}
                </span>
                <span style={{ 
                  fontSize: '0.74rem', 
                  fontFamily: 'var(--font-mono)', 
                  color: c.passed ? '#10b981' : '#f43f5e',
                  background: c.passed ? 'rgba(16, 185, 129, 0.1)' : 'rgba(244, 63, 94, 0.1)',
                  padding: '2px 8px',
                  borderRadius: '4px'
                }}>
                  {c.passed ? 'PASSED' : 'VIOLATION'}
                </span>
              </div>
              <div style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', marginTop: 2 }}>
                {c.detail}
              </div>
            </div>
          </div>
        ))}
      </div>

      <div style={{ 
        marginTop: 14, 
        padding: '10px 14px', 
        borderRadius: 'var(--radius-sm)', 
        background: decision === 'AUTO-HANDLE' ? 'rgba(16, 185, 129, 0.08)' : 'rgba(244, 63, 94, 0.08)',
        border: `1px solid ${decision === 'AUTO-HANDLE' ? 'rgba(16, 185, 129, 0.2)' : 'rgba(244, 63, 94, 0.2)'}`,
        fontSize: '0.82rem',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between'
      }}>
        <span style={{ color: 'var(--text-secondary)' }}>Final Grounding Decision:</span>
        <strong style={{ color: decision === 'AUTO-HANDLE' ? '#10b981' : '#f43f5e' }}>
          {decision === 'AUTO-HANDLE' ? 'Safe to Auto-Reply' : 'Human Routing Enforced'}
        </strong>
      </div>
    </div>
  );
}
