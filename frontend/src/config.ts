/**
 * Configuration for the frontend application.
 */

// API base URL - uses proxy in development and production (nginx proxies /api to backend)
// Empty string means relative URLs like "/api/issues" which nginx will proxy to backend
export const API_BASE_URL = import.meta.env.PROD 
  ? (import.meta.env.VITE_API_URL !== undefined ? import.meta.env.VITE_API_URL : 'http://localhost:8000')
  : '';

// Polling interval for activity feed (milliseconds)
export const ACTIVITY_POLL_INTERVAL = 5000;

// Polling interval for metrics (milliseconds)
export const METRICS_POLL_INTERVAL = 10000;
