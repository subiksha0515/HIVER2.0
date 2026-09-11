import React, { useState, useEffect } from 'react';
import Analyze from './pages/Analyze';
import Dashboard from './pages/Dashboard';

export default function App() {
  const [activeTab, setActiveTab] = useState('analyze'); // 'analyze' or 'dashboard'
  const [backendReady, setBackendReady] = useState(false);
  const [systemInfo, setSystemInfo] = useState(null);

  useEffect(() => {
    // Check backend health and status
    const checkStatus = async () => {
      try {
        const res = await fetch('/api/status');
        if (res.ok) {
          const data = await res.json();
          setBackendReady(true);
          setSystemInfo(data);
        } else {
          setBackendReady(false);
        }
      } catch (err) {
        setBackendReady(false);
      }
    };

    checkStatus();
    const interval = setInterval(checkStatus, 15000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="app-container">
      {/* Top Navigation Header */}
      <header className="navbar">
        <div className="nav-brand">
          <div className="brand-icon">
            <span>🛡️</span>
          </div>
          <div>
            <div className="brand-title">AI Support Decision Engine</div>
            <div className="brand-subtitle">
              Deterministic Safety Escalation & Grounded Historical Retrieval
            </div>
          </div>
        </div>

        <div className="nav-links">
          <button
            type="button"
            className={`nav-tab ${activeTab === 'analyze' ? 'active' : ''}`}
            onClick={() => setActiveTab('analyze')}
          >
            Query Decision Engine
          </button>
          <button
            type="button"
            className={`nav-tab ${activeTab === 'dashboard' ? 'active' : ''}`}
            onClick={() => setActiveTab('dashboard')}
          >
            Evaluation Dashboard
          </button>
        </div>

        <div>
          <div 
            className="status-badge"
            style={{
              borderColor: backendReady ? 'var(--success-border)' : 'var(--danger-border)',
              background: backendReady ? 'var(--success-bg)' : 'var(--danger-bg)',
              color: backendReady ? 'var(--success)' : 'var(--danger)'
            }}
          >
            <span 
              className="status-dot" 
              style={{
                background: backendReady ? 'var(--success)' : 'var(--danger)',
                boxShadow: backendReady ? '0 0 8px var(--success)' : '0 0 8px var(--danger)'
              }} 
            />
            <span>{backendReady ? 'API Ready' : 'Backend Connecting'}</span>
          </div>
        </div>
      </header>

      {/* Main Content Pages */}
      <main>
        {activeTab === 'analyze' && <Analyze />}
        {activeTab === 'dashboard' && <Dashboard />}
      </main>
    </div>
  );
}
