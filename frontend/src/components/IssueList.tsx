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
  const [repoUrl, setRepoUrl] = useState<string>('');
  const [showScanDialog, setShowScanDialog] = useState(false);

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

  const handleScanRepository = async (customRepoUrl?: string) => {
    let repoOwner: string | undefined;
    let repoName: string | undefined;

    // Parse GitHub URL if provided
    if (customRepoUrl) {
      const match = customRepoUrl.match(/github\.com\/([^\/]+)\/([^\/\?#]+)/);
      if (!match) {
        alert('Invalid GitHub URL. Format: https://github.com/owner/repo');
        return;
      }
      repoOwner = match[1];
      repoName = match[2].replace(/\.git$/, ''); // Remove .git suffix if present
    }

    const repoDisplay = customRepoUrl ? `${repoOwner}/${repoName}` : 'your configured repository';
    if (!confirm(`This will scan ${repoDisplay} with SonarQube. It may take a few minutes. Continue?`)) {
      return;
    }
    
    try {
      setLoading(true);
      setShowScanDialog(false);
      const result = await apiClient.scanRepository(repoOwner, repoName);
      alert(`${result.message}\n\nView results at: ${result.project_url || 'SonarQube dashboard'}`);
      // After scanning, sync issues
      await handleSyncIssues();
    } catch (err) {
      alert(`Error: ${err instanceof Error ? err.message : 'Unknown error'}`);
      setLoading(false);
    }
  };

  const handleFixAll = async () => {
    const newIssues = issues.filter(i => i.status === IssueStatus.NEW);
    if (newIssues.length === 0) {
      alert('No new issues to fix!');
      return;
    }

    if (!confirm(`This will trigger AI fixes for ${newIssues.length} issues. This may take several minutes. Continue?`)) {
      return;
    }

    try {
      setLoading(true);
      let successCount = 0;
      let errorCount = 0;

      for (const issue of newIssues) {
        try {
          await apiClient.triggerFix(issue.id);
          successCount++;
        } catch (err) {
          console.error(`Failed to fix issue ${issue.id}:`, err);
          errorCount++;
        }
      }

      alert(`Fix All completed!\n\nSuccessful: ${successCount}\nFailed: ${errorCount}`);
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
            <option value="CI_PASSED">Merged</option>
            <option value="CI_FAILED">Not Merged</option>
            <option value="CLOSED">Closed</option>
          </select>
          <button 
            className="button button-primary button-small"
            onClick={() => setShowScanDialog(true)}
            disabled={loading}
          >
            🔎 Scan Repository
          </button>
          <button 
            className="button button-secondary button-small"
            onClick={handleSyncIssues}
            disabled={loading}
          >
            Sync from SonarQube
          </button>
          {issues.filter((i: Issue) => i.status === IssueStatus.NEW).length > 0 && (
            <button 
              className="button button-primary button-small"
              onClick={handleFixAll}
              disabled={loading}
              style={{ backgroundColor: '#10b981' }}
            >
              🤖 Fix All ({issues.filter((i: Issue) => i.status === IssueStatus.NEW).length})
            </button>
          )}
        </div>
      </div>

      {/* Scan Repository Dialog */}
      {showScanDialog && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundColor: 'rgba(0,0,0,0.5)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1000
        }}>
          <div style={{
            backgroundColor: 'white',
            padding: '2rem',
            borderRadius: '8px',
            maxWidth: '500px',
            width: '90%'
          }}>
            <h3 style={{ marginTop: 0 }}>Scan Repository</h3>
            <p style={{ fontSize: '0.875rem', color: '#666' }}>
              Leave blank to scan your configured repository, or enter a GitHub URL to scan any public repository.
            </p>
            <p style={{ fontSize: '0.75rem', color: '#f59e0b', marginTop: '0.5rem', padding: '0.5rem', backgroundColor: '#fffbeb', borderRadius: '4px', border: '1px solid #fef3c7' }}>
              ⚠️ External repos: Read-only mode. You can view issues but cannot create PRs without write access.
            </p>
            <input
              type="text"
              placeholder="https://github.com/owner/repo (optional)"
              value={repoUrl}
              onChange={(e) => setRepoUrl(e.target.value)}
              style={{
                width: '100%',
                padding: '0.75rem',
                borderRadius: '4px',
                border: '1px solid #ddd',
                marginBottom: '1rem',
                fontSize: '0.875rem'
              }}
            />
            <div style={{ display: 'flex', gap: '0.5rem', justifyContent: 'flex-end' }}>
              <button
                className="button button-secondary"
                onClick={() => {
                  setShowScanDialog(false);
                  setRepoUrl('');
                }}
              >
                Cancel
              </button>
              <button
                className="button button-primary"
                onClick={() => {
                  handleScanRepository(repoUrl || undefined);
                  setRepoUrl('');
                }}
              >
                Scan
              </button>
            </div>
          </div>
        </div>
      )}

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
