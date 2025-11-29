/**
 * API client for communicating with the backend.
 */

import { API_BASE_URL } from './config';
import type {
  IssueDetail,
  IssueListResponse,
  Event,
  MetricsSummary,
  TriggerFixResponse,
} from './types';

class ApiClient {
  private baseUrl: string;

  constructor() {
    this.baseUrl = API_BASE_URL;
  }

  private async request<T>(
    endpoint: string,
    options?: RequestInit
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    
    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
      throw new Error(error.detail || `HTTP ${response.status}`);
    }

    return response.json();
  }

  // Issues
  async getIssues(params?: {
    page?: number;
    page_size?: number;
    status?: string;
    severity?: string;
  }): Promise<IssueListResponse> {
    const searchParams = new URLSearchParams();
    if (params?.page) searchParams.set('page', params.page.toString());
    if (params?.page_size) searchParams.set('page_size', params.page_size.toString());
    if (params?.status) searchParams.set('status', params.status);
    if (params?.severity) searchParams.set('severity', params.severity);

    const query = searchParams.toString() ? `?${searchParams.toString()}` : '';
    return this.request<IssueListResponse>(`/api/issues${query}`);
  }

  async getIssue(issueId: string): Promise<IssueDetail> {
    return this.request<IssueDetail>(`/api/issues/${issueId}`);
  }

  async triggerFix(issueId: string): Promise<TriggerFixResponse> {
    return this.request<TriggerFixResponse>(`/api/issues/${issueId}/trigger-fix`, {
      method: 'POST',
    });
  }

  // Events
  async getRecentEvents(limit: number = 50): Promise<Event[]> {
    return this.request<Event[]>(`/api/events/recent?limit=${limit}`);
  }

  // Metrics
  async getMetricsSummary(): Promise<MetricsSummary> {
    return this.request<MetricsSummary>('/api/metrics/summary');
  }

  // Sync
  async syncIssues(): Promise<{ success: boolean; message: string; new_issues: number }> {
    return this.request('/api/sync', {
      method: 'POST',
    });
  }
}

export const apiClient = new ApiClient();
