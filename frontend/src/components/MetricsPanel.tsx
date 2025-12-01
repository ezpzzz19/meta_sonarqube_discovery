/**
 * Metrics panel component showing aggregate statistics.
 */

import { useEffect, useState } from 'react';
import { apiClient } from '../api';
import type { MetricsSummary } from '../types';
import { METRICS_POLL_INTERVAL } from '../config';

export function MetricsPanel() {
  const [metrics, setMetrics] = useState<MetricsSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        const data = await apiClient.getMetricsSummary();
        setMetrics(data);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch metrics');
      } finally {
        setLoading(false);
      }
    };

    fetchMetrics();
    const interval = setInterval(fetchMetrics, METRICS_POLL_INTERVAL);

    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="card">
        <div className="loading">Loading metrics...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="card">
        <div className="error">{error}</div>
      </div>
    );
  }

  if (!metrics) return null;

  return (
    <div className="metrics-grid">
      <div className="metric-card">
        <div className="metric-value">{metrics.total_issues}</div>
        <div className="metric-label">Total Issues</div>
      </div>
      
      <div className="metric-card">
        <div className="metric-value">{metrics.new_issues}</div>
        <div className="metric-label">New Issues</div>
      </div>
      
      <div className="metric-card" style={{ backgroundColor: '#f59e0b20', borderLeft: '4px solid #f59e0b' }}>
        <div className="metric-value" style={{ color: '#f59e0b' }}>{metrics.pr_open_issues}</div>
        <div className="metric-label">Open PRs</div>
        <div style={{ fontSize: '0.7rem', color: '#6b7280', marginTop: '0.25rem' }}>
          (Pending Review)
        </div>
      </div>

      <div className="metric-card" style={{ backgroundColor: '#10b98120', borderLeft: '4px solid #10b981' }}>
        <div className="metric-value" style={{ color: '#10b981' }}>{metrics.merged_prs}</div>
        <div className="metric-label">Merged PRs</div>
        <div style={{ fontSize: '0.7rem', color: '#6b7280', marginTop: '0.25rem' }}>
          (Success ✓)
        </div>
      </div>
      
      <div className="metric-card" style={{ backgroundColor: '#ef444420', borderLeft: '4px solid #ef4444' }}>
        <div className="metric-value" style={{ color: '#ef4444' }}>{metrics.rejected_prs}</div>
        <div className="metric-label">Rejected PRs</div>
        <div style={{ fontSize: '0.7rem', color: '#6b7280', marginTop: '0.25rem' }}>
          (Closed/Not Merged)
        </div>
      </div>
      
      <div className="metric-card" style={{ backgroundColor: '#3b82f620' }}>
        <div className="metric-value" style={{ color: '#3b82f6' }}>{metrics.success_rate}%</div>
        <div className="metric-label">Success Rate</div>
        <div style={{ fontSize: '0.7rem', color: '#6b7280', marginTop: '0.25rem' }}>
          (Merged / Completed)
        </div>
      </div>
    </div>
  );
}
