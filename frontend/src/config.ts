/**
 * Configuration for the frontend application.
 */

// API base URL - uses proxy in development, direct URL in production
export const API_BASE_URL = import.meta.env.PROD 
  ? (import.meta.env.VITE_API_URL || 'http://localhost:8000')
  : '';

// Polling interval for activity feed (milliseconds)
export const ACTIVITY_POLL_INTERVAL = 5000;

// Polling interval for metrics (milliseconds)
export const METRICS_POLL_INTERVAL = 10000;
