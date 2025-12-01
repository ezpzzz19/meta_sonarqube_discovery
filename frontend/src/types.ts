/**
 * TypeScript types for API responses.
 */

export enum IssueStatus {
  NEW = 'NEW',
  FIXING = 'FIXING',
  PR_OPEN = 'PR_OPEN',
  CI_PASSED = 'CI_PASSED',
  CI_FAILED = 'CI_FAILED',
  CLOSED = 'CLOSED',
}

export enum EventType {
  ISSUE_DETECTED = 'ISSUE_DETECTED',
  AI_CALLED = 'AI_CALLED',
  PR_CREATED = 'PR_CREATED',
  CI_PASSED = 'CI_PASSED',
  CI_FAILED = 'CI_FAILED',
  STATUS_UPDATED = 'STATUS_UPDATED',
  ERROR = 'ERROR',
}

export interface Issue {
  id: string;
  sonarqube_issue_key: string;
  project_key: string;
  rule: string;
  severity: string;
  component: string;
  line: number | null;
  message: string | null;
  status: IssueStatus;
  pr_url: string | null;
  pr_branch: string | null;
  pr_merged: number; // 0=not merged, 1=merged, -1=unknown/no PR
  created_at: string;
  updated_at: string;
}

export interface Event {
  id: string;
  issue_id: string;
  event_type: EventType;
  message: string;
  metadata: string | null;
  created_at: string;
}

export interface IssueDetail extends Issue {
  events: Event[];
}

export interface IssueListResponse {
  items: Issue[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface MetricsSummary {
  total_issues: number;
  new_issues: number;
  fixing_issues: number;
  pr_open_issues: number;
  ci_passed_issues: number;
  ci_failed_issues: number;
  closed_issues: number;
  total_prs_created: number;
  merged_prs: number;
  rejected_prs: number;
  success_rate: number;
}

export interface TriggerFixResponse {
  success: boolean;
  message: string;
  issue_id: string;
}
