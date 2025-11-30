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
        <div className="metric-label">New</div>
      </div>
      
      <div className="metric-card">
        <div className="metric-value">{metrics.pr_open_issues}</div>
        <div className="metric-label">PR Open</div>
      </div>
      
      <div className="metric-card">
        <div className="metric-value">{metrics.ci_passed_issues}</div>
        <div className="metric-label">Merged</div>
      </div>
      
      <div className="metric-card">
        <div className="metric-value">{metrics.total_prs_created}</div>
        <div className="metric-label">Total PRs</div>
      </div>
      
      <div className="metric-card">
        <div className="metric-value">{metrics.success_rate}%</div>
        <div className="metric-label">Success Rate</div>
      </div>
    </div>
  );
}
