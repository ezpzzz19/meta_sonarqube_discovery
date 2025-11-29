/**
 * Activity feed component showing recent events.
 */

import { useEffect, useState } from 'react';
import { apiClient } from '../api';
import type { Event } from '../types';
import { ACTIVITY_POLL_INTERVAL } from '../config';

export function ActivityFeed() {
  const [events, setEvents] = useState<Event[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchEvents = async () => {
      try {
        const data = await apiClient.getRecentEvents(30);
        setEvents(data);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch events');
      } finally {
        setLoading(false);
      }
    };

    fetchEvents();
    const interval = setInterval(fetchEvents, ACTIVITY_POLL_INTERVAL);

    return () => clearInterval(interval);
  }, []);

  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const minutes = Math.floor(diff / 60000);
    
    if (minutes < 1) return 'Just now';
    if (minutes < 60) return `${minutes}m ago`;
    const hours = Math.floor(minutes / 60);
    if (hours < 24) return `${hours}h ago`;
    const days = Math.floor(hours / 24);
    return `${days}d ago`;
  };

  const getEventIcon = (eventType: string) => {
    switch (eventType) {
      case 'ISSUE_DETECTED': return '🔍';
      case 'AI_CALLED': return '🤖';
      case 'PR_CREATED': return '📝';
      case 'CI_PASSED': return '✅';
      case 'CI_FAILED': return '❌';
      case 'STATUS_UPDATED': return '🔄';
      case 'ERROR': return '⚠️';
      default: return '📌';
    }
  };

  if (loading) {
    return (
      <div className="card">
        <h2 className="card-title">Activity Feed</h2>
        <div className="loading">Loading events...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="card">
        <h2 className="card-title">Activity Feed</h2>
        <div className="error">{error}</div>
      </div>
    );
  }

  return (
    <div className="card">
      <h2 className="card-title">Activity Feed</h2>
      {events.length === 0 ? (
        <div className="empty-state">
          <div className="empty-state-icon">📋</div>
          <div className="empty-state-text">No recent activity</div>
        </div>
      ) : (
        <div className="activity-feed">
          {events.map((event) => (
            <div key={event.id} className="activity-item">
              <div className="activity-type">
                {getEventIcon(event.event_type)} {event.event_type.replace(/_/g, ' ')}
              </div>
              <div className="activity-message">{event.message}</div>
              <div className="activity-time">{formatTime(event.created_at)}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
