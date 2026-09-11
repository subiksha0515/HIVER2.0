import React from 'react';

export default function DecisionPanel({ decision, reason, stage }) {
  if (!decision) return null;

  const isAuto = decision === 'AUTO-HANDLE';

  return (
    <div className={`decision-banner ${isAuto ? 'auto' : 'escalate'}`}>
      <div>
        <div className="decision-badge">
          <span>{isAuto ? '⚡' : '🛡️'}</span>
          <span>{isAuto ? 'AUTO-HANDLE' : 'ESCALATE TO HUMAN'}</span>
        </div>
        
        {reason && (
          <div className="escalation-reason-box">
            <strong>Escalation Reason:</strong> {reason}
          </div>
        )}

        <div style={{ fontSize: '0.78rem', color: isAuto ? '#a7f3d0' : '#fbcfe8', marginTop: 6 }}>
          {isAuto 
            ? 'Query passed all 6 deterministic safety checks. Safe for autonomous delivery.' 
            : 'Escalated to human support queue to prevent ungrounded action or hallucination.'}
        </div>
      </div>

      <div style={{ textAlign: 'right', display: 'none', md: 'block' }}>
        <span style={{ 
          fontSize: '0.72rem', 
          fontFamily: 'var(--font-mono)', 
          padding: '4px 10px', 
          borderRadius: '4px',
          background: 'rgba(0,0,0,0.3)',
          color: '#ffffff'
        }}>
          STAGE: {stage || 'COMPLETED'}\n        </span>
      </div>
    </div>
  );
}
