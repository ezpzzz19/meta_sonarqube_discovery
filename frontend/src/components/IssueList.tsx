/**
 * Issue list component showing all issues in a table.
 */

import { useEffect, useState } from 'react';
import { apiClient } from '../api';
import type { Issue } from '../types';
import { IssueStatus } from '../types';

export function IssueList() {
  const [issues, setIssues] = useState<Issue[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [triggeringFix, setTriggeringFix] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [statusFilter, setStatusFilter] = useState<string>('');

  const fetchIssues = async () => {
    try {
      const data = await apiClient.getIssues({
        page,
        page_size: 20,
        status: statusFilter || undefined,
      });
      setIssues(data.items);
      setTotalPages(data.total_pages);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch issues');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    setLoading(true);
    fetchIssues();
  }, [page, statusFilter]);

  const handleTriggerFix = async (issueId: string) => {
    setTriggeringFix(issueId);
    try {
      const result = await apiClient.triggerFix(issueId);
      if (result.success) {
        // Refresh the list
        await fetchIssues();
      } else {
        alert(`Failed to trigger fix: ${result.message}`);
      }
    } catch (err) {
      alert(`Error: ${err instanceof Error ? err.message : 'Unknown error'}`);
    } finally {
      setTriggeringFix(null);
    }
  };

  const handleSyncIssues = async () => {
    try {
      setLoading(true);
      const result = await apiClient.syncIssues();
      alert(result.message);
      await fetchIssues();
    } catch (err) {
      alert(`Error: ${err instanceof Error ? err.message : 'Unknown error'}`);
    } finally {
      setLoading(false);
    }
  };

  const getStatusClass = (status: IssueStatus) => {
    return `status-badge status-${status.toLowerCase()}`;
  };

  const getSeverityClass = (severity: string) => {
    return `severity-badge severity-${severity.toLowerCase()}`;
  };

  if (loading && issues.length === 0) {
    return (
      <div className="card">
        <h2 className="card-title">Issues</h2>
        <div className="loading">Loading issues...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="card">
        <h2 className="card-title">Issues</h2>
        <div className="error">{error}</div>
      </div>
    );
  }

  return (
    <div className="card">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
        <h2 className="card-title" style={{ marginBottom: 0 }}>Issues</h2>
        <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
          <select 
            value={statusFilter} 
            onChange={(e) => {
              setStatusFilter(e.target.value);
              setPage(1);
            }}
            style={{ padding: '0.5rem', borderRadius: '4px', border: '1px solid #ddd' }}
          >
            <option value="">All Statuses</option>
            <option value="NEW">New</option>
            <option value="FIXING">Fixing</option>
            <option value="PR_OPEN">PR Open</option>
            <option value="CI_PASSED">CI Passed</option>
            <option value="CI_FAILED">CI Failed</option>
            <option value="CLOSED">Closed</option>
          </select>
          <button 
            className="button button-secondary button-small"
            onClick={handleSyncIssues}
            disabled={loading}
          >
            Sync from SonarQube
          </button>
        </div>
      </div>

      {issues.length === 0 ? (
        <div className="empty-state">
          <div className="empty-state-icon">🔍</div>
          <div className="empty-state-text">No issues found</div>
        </div>
      ) : (
        <>
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>Issue Key</th>
                  <th>Severity</th>
                  <th>Rule</th>
                  <th>File</th>
                  <th>Line</th>
                  <th>Status</th>
                  <th>PR</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {issues.map((issue) => (
                  <tr key={issue.id}>
                    <td>
                      <span className="code">{issue.sonarqube_issue_key}</span>
                    </td>
                    <td>
                      <span className={getSeverityClass(issue.severity)}>
                        {issue.severity}
                      </span>
                    </td>
                    <td style={{ fontSize: '0.875rem' }}>{issue.rule}</td>
                    <td style={{ fontSize: '0.875rem' }}>
                      <span className="code">{issue.component}</span>
                    </td>
                    <td>{issue.line || '-'}</td>
                    <td>
                      <span className={getStatusClass(issue.status)}>
                        {issue.status}
                      </span>
                    </td>
                    <td>
                      {issue.pr_url ? (
                        <a href={issue.pr_url} target="_blank" rel="noopener noreferrer">
                          View PR
                        </a>
                      ) : (
                        '-'
                      )}
                    </td>
                    <td>
                      {issue.status === IssueStatus.NEW && (
                        <button
                          className="button button-primary button-small"
                          onClick={() => handleTriggerFix(issue.id)}
                          disabled={triggeringFix === issue.id}
                        >
                          {triggeringFix === issue.id ? 'Fixing...' : 'Trigger AI Fix'}
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {totalPages > 1 && (
            <div style={{ display: 'flex', justifyContent: 'center', gap: '0.5rem', marginTop: '1rem' }}>
              <button
                className="button button-secondary button-small"
                onClick={() => setPage(p => Math.max(1, p - 1))}
                disabled={page === 1}
              >
                Previous
              </button>
              <span style={{ padding: '0.5rem 1rem', fontSize: '0.875rem' }}>
                Page {page} of {totalPages}
              </span>
              <button
                className="button button-secondary button-small"
                onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                disabled={page === totalPages}
              >
                Next
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
}
