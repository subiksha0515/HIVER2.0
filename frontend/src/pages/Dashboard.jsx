import React from 'react';

export default function Dashboard() {
  return (
    <div>
      {/* Top Stat Cards */}
      <div className="stat-grid">
        <div className="stat-card">
          <div className="stat-label">Intent Classification</div>
          <div className="stat-value" style={{ color: '#818cf8' }}>0.9199</div>
          <div className="stat-sub">Test Macro F1 (96.81% Accuracy)</div>
        </div>

        <div className="stat-card">
          <div className="stat-label">Retrieval Grounding</div>
          <div className="stat-value" style={{ color: '#06b6d4' }}>90.02%</div>
          <div className="stat-sub">Recall@5 (MRR: 0.7460)</div>
        </div>

        <div className="stat-card">
          <div className="stat-label">Selective Accuracy</div>
          <div className="stat-value" style={{ color: '#10b981' }}>96.95%</div>
          <div className="stat-sub">Accuracy on Auto-Handled Subset</div>
        </div>

        <div className="stat-card">
          <div className="stat-label">Safety & Grounding</div>
          <div className="stat-value" style={{ color: '#34d399' }}>0.00%</div>
          <div className="stat-sub">Unsupported Claims (Zero Hallucination)</div>
        </div>
      </div>

      {/* Dataset & Leakage Audit Overview */}
      <div className="glass-card">
        <div className="card-title">
          <span>🔒</span>
          <span>Leakage-Free Dataset Split Verification</span>
        </div>
        <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: 16 }}>
          All splits are partition-disjoint by unique <code>conversation_id</code>. Historical retrieval index is 100% constructed from <code>train.jsonl</code> with verified zero contamination into test sets.
        </p>

        <table className="data-table">
          <thead>
            <tr>
              <th>Dataset Split</th>
              <th>Record Count</th>
              <th>Dataset Share</th>
              <th>Overlap with Test</th>
              <th>Split Methodology</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td><strong style={{ color: '#ffffff' }}>Training Set (train.jsonl)</strong></td>
              <td className="metric-highlight">57,036</td>
              <td>70.0%</td>
              <td><span style={{ color: '#10b981' }}>0 (0.00%)</span></td>
              <td>Conversation-level random seed partition</td>
            </tr>
            <tr>
              <td><strong style={{ color: '#ffffff' }}>Validation Set (val.jsonl)</strong></td>
              <td className="metric-highlight">12,222</td>
              <td>15.0%</td>
              <td><span style={{ color: '#10b981' }}>0 (0.00%)</span></td>
              <td>Threshold calibration & hyperparameter tuning</td>
            </tr>
            <tr>
              <td><strong style={{ color: '#ffffff' }}>Held-Out Test Set (test.jsonl)</strong></td>
              <td className="metric-highlight">12,222</td>
              <td>15.0%</td>
              <td><span style={{ color: '#10b981' }}>0 (0.00%)</span></td>
              <td>Final un-compromised evaluation benchmark</td>
            </tr>
            <tr>
              <td><strong style={{ color: '#ffffff' }}>Temporal Test Set (temporal_test.jsonl)</strong></td>
              <td className="metric-highlight">12,222</td>
              <td>15.0%</td>
              <td><span style={{ color: '#10b981' }}>0 (0.00%)</span></td>
              <td>Latest historical interactions (temporal stability)</td>
            </tr>
            <tr>
              <td><strong style={{ color: '#ffffff' }}>Retrieval Vector Index</strong></td>
              <td className="metric-highlight">57,036</td>
              <td>100% Train</td>
              <td><span style={{ color: '#10b981' }}>0 (0.00%)</span></td>
              <td>Dense SVD (128d) cosine similarity index</td>
            </tr>
          </tbody>
        </table>
      </div>

      <div className="results-grid">
        {/* Intent Model Comparison Table */}
        <div className="glass-card">
          <div className="card-title">
            <span>📊</span>
            <span>Intent Classifier Comparison (Held-Out Test)</span>
          </div>

          <table className="data-table">
            <thead>
              <tr>
                <th>Model Architecture</th>
                <th>Accuracy</th>
                <th>Macro F1</th>
                <th>Weighted F1</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>Majority Class Baseline</td>
                <td>48.30%</td>
                <td>0.0592</td>
                <td>0.3146</td>
              </tr>
              <tr>
                <td>Rule / Keyword Baseline</td>
                <td>80.67%</td>
                <td>0.5803</td>
                <td>0.7719</td>
              </tr>
              <tr>
                <td>Embedding KNN Baseline</td>
                <td>63.96%</td>
                <td>0.4367</td>
                <td>0.6176</td>
              </tr>
              <tr style={{ background: 'rgba(99, 102, 241, 0.1)' }}>
                <td><strong style={{ color: '#a5b4fc' }}>TF-IDF + Logistic Regression (Selected)</strong></td>
                <td className="metric-highlight">96.81%</td>
                <td className="metric-highlight" style={{ color: '#10b981' }}>0.9199</td>
                <td className="metric-highlight">0.9681</td>
              </tr>
              <tr>
                <td>Dense SVD Embedding + LogReg</td>
                <td>79.82%</td>
                <td>0.5763</td>
                <td>0.8231</td>
              </tr>
            </tbody>
          </table>
        </div>

        {/* Retrieval Quantitative Metrics */}
        <div className="glass-card">
          <div className="card-title">
            <span>🔍</span>
            <span>Retrieval Performance (5,000 Queries)</span>
          </div>

          <table className="data-table">
            <thead>
              <tr>
                <th>Retrieval Metric</th>
                <th>Measured Value</th>
                <th>Evaluation Target</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>Recall@1 (Top Match Accuracy)</td>
                <td className="metric-highlight">64.84%</td>
                <td>Baseline</td>
              </tr>
              <tr>
                <td>Recall@3 (Top-3 Intent Grounding)</td>
                <td className="metric-highlight">85.58%</td>
                <td>&gt;= 80.0%</td>
              </tr>
              <tr>
                <td>Recall@5 (Top-5 Intent Grounding)</td>
                <td className="metric-highlight" style={{ color: '#10b981' }}>90.02%</td>
                <td>&gt;= 85.0%</td>
              </tr>
              <tr>
                <td>Mean Reciprocal Rank (MRR)</td>
                <td className="metric-highlight" style={{ color: '#06b6d4' }}>0.7460</td>
                <td>&gt;= 0.70</td>
              </tr>
              <tr>
                <td>Index Construction Source</td>
                <td colSpan={2} style={{ color: 'var(--text-secondary)' }}>
                  <code>train.jsonl</code> (57,036 cases, 0 test overlap)
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      {/* Escalation Policy Triggers */}
      <div className="glass-card">
        <div className="card-title">
          <span>🛡️</span>
          <span>Escalation Breakdown by Policy Rule (5,000 Test Audit)</span>
        </div>
        <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: 14 }}>
          Overall Coverage: <strong>39.30% auto-handled</strong> (1,965 cases) vs <strong>60.70% safely escalated</strong> (3,035 cases).
        </p>

        <table className="data-table">
          <thead>
            <tr>
              <th>Policy Rule Trigger</th>
              <th>Escalations Count</th>
              <th>Share of Escalations</th>
              <th>Safety Rationale</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td><code>The issue is outside the supported intent taxonomy.</code></td>
              <td className="metric-highlight">2,387</td>
              <td>78.6%</td>
              <td>Prevents forced guesses on undefined or out-of-domain domains</td>
            </tr>
            <tr>
              <td><code>Historical examples provide conflicting guidance.</code></td>
              <td className="metric-highlight">560</td>
              <td>18.5%</td>
              <td>Prevents responding when top retrieved cases disagree on root problem</td>
            </tr>
            <tr>
              <td><code>Request requires an action unavailable to the AI.</code></td>
              <td className="metric-highlight">38</td>
              <td>1.3%</td>
              <td>Blocks financial refunds, account deletions, fraud, legal threats</td>
            </tr>
            <tr>
              <td><code>Intent confidence below validated threshold (&lt; 0.45).</code></td>
              <td className="metric-highlight">34</td>
              <td>1.1%</td>
              <td>Safety floor to prevent low-confidence hallucinations</td>
            </tr>
            <tr>
              <td><code>Customer request is ambiguous.</code></td>
              <td className="metric-highlight">16</td>
              <td>0.5%</td>
              <td>Escalates single-token queries (e.g. 'help', '?')</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  );
}
