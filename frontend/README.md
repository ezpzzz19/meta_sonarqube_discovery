# Frontend - SonarQube Code Janitor Dashboard

React + TypeScript dashboard for monitoring and controlling the AI code fixer.

## 🎨 Overview

A clean, responsive dashboard that provides real-time visibility into the code fixing process.

### Features

- **📊 Metrics Panel**: Real-time statistics with auto-refresh
- **📋 Issue List**: Sortable, filterable table of all issues
- **🔄 Activity Feed**: Live event stream
- **🎯 Manual Controls**: Trigger fixes and sync issues on-demand

## 🚀 Quick Start

### Development

```bash
# Install dependencies
npm install

# Start dev server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

The app will be available at http://localhost:3000

### Production Build

```bash
# Build optimized bundle
npm run build

# Output in dist/ directory
```

## 📁 Project Structure

```
src/
├── components/           # React components
│   ├── IssueList.tsx    # Main issue table
│   ├── ActivityFeed.tsx # Event timeline
│   └── MetricsPanel.tsx # Statistics cards
├── api.ts               # API client
├── types.ts             # TypeScript interfaces
├── config.ts            # Configuration
├── App.tsx              # Main app component
├── App.css              # Global styles
└── main.tsx             # Entry point
```

## 🎯 Components

### IssueList

Displays all SonarQube issues in a table format.

**Features:**
- Pagination (20 items per page)
- Status filter dropdown
- Manual sync button
- Trigger AI fix button for NEW issues
- Direct links to SonarQube and GitHub PRs

**Status Badge Colors:**
- 🔵 NEW - Blue
- 🟠 FIXING - Orange
- 🟣 PR_OPEN - Purple
- 🟢 CI_PASSED - Green
- 🔴 CI_FAILED - Red
- ⚫ CLOSED - Gray

### ActivityFeed

Live feed of events across all issues.

**Features:**
- Auto-refresh every 5 seconds
- Shows last 30 events
- Event icons for visual identification
- Relative timestamps ("5m ago", "2h ago")

**Event Types:**
- 🔍 ISSUE_DETECTED
- 🤖 AI_CALLED
- 📝 PR_CREATED
- ✅ CI_PASSED
- ❌ CI_FAILED
- 🔄 STATUS_UPDATED
- ⚠️ ERROR

### MetricsPanel

Dashboard-style metrics overview.

**Metrics Displayed:**
- Total Issues
- New Issues
- PR Open
- CI Passed
- Total PRs Created
- Success Rate %

**Refresh:** Auto-updates every 10 seconds

## 🔧 Configuration

### Environment Variables

Create `.env` file (optional, for production):

```bash
VITE_API_URL=http://your-backend-url:8000
```

In development, the Vite proxy handles API calls automatically.

### API Configuration

Edit `src/config.ts`:

```typescript
// API base URL
export const API_BASE_URL = import.meta.env.PROD 
  ? (import.meta.env.VITE_API_URL || 'http://localhost:8000')
  : '';

// Polling intervals (milliseconds)
export const ACTIVITY_POLL_INTERVAL = 5000;
export const METRICS_POLL_INTERVAL = 10000;
```

## 🎨 Styling

### CSS Architecture

- `App.css` - Global styles and utility classes
- Component-specific styles are inline or in the main CSS
- CSS variables for consistent theming

### Key Classes

```css
.status-badge       /* Issue status indicators */
.severity-badge     /* Severity indicators */
.metric-card        /* Metric display cards */
.activity-item      /* Event feed items */
.button-primary     /* Primary action button */
.button-secondary   /* Secondary action button */
```

### Color Scheme

```css
Primary: #3498db (Blue)
Success: #388e3c (Green)
Warning: #f57c00 (Orange)
Error: #d32f2f (Red)
Background: #f5f5f5
Text: #333
```

## 📡 API Integration

### API Client (`src/api.ts`)

Provides typed methods for all backend endpoints:

```typescript
// Get issues with filters
await apiClient.getIssues({
  page: 1,
  page_size: 20,
  status: 'NEW',
  severity: 'MAJOR'
});

// Get issue details
await apiClient.getIssue(issueId);

// Trigger fix
await apiClient.triggerFix(issueId);

// Get recent events
await apiClient.getRecentEvents(50);

// Get metrics
await apiClient.getMetricsSummary();

// Sync issues
await apiClient.syncIssues();
```

### Type Safety

All API responses are typed using interfaces from `src/types.ts`:

```typescript
interface Issue {
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
  created_at: string;
  updated_at: string;
}
```

## 🔄 Real-Time Updates

### Polling Strategy

The app uses polling for real-time updates (no WebSockets needed for this demo):

- **Activity Feed**: 5 seconds
- **Metrics Panel**: 10 seconds
- **Issue List**: Manual refresh (after actions)

### Implementing Updates

```typescript
useEffect(() => {
  const fetchData = async () => {
    const data = await apiClient.getRecentEvents();
    setEvents(data);
  };

  fetchData();
  const interval = setInterval(fetchData, 5000);
  
  return () => clearInterval(interval);
}, []);
```

## 🧪 Development Tips

### Hot Reload

Vite provides instant hot module replacement. Changes to React components, CSS, and TypeScript files update immediately.

### API Mocking

For development without backend:

```typescript
// In src/api.ts
const MOCK_MODE = false;

if (MOCK_MODE) {
  return Promise.resolve(mockData);
}
```

### Debugging

```typescript
// Enable API logging
console.log('API Request:', endpoint, options);
console.log('API Response:', response);
```

### Browser DevTools

- React DevTools extension for component inspection
- Network tab to monitor API calls
- Console for error messages

## 📱 Responsive Design

The dashboard is responsive and works on:
- Desktop (1400px+)
- Laptop (1024px+)
- Tablet (768px+)
- Mobile (320px+)

### Breakpoints

```css
@media (max-width: 1024px) {
  .main-content {
    grid-template-columns: 1fr;  /* Stack vertically */
  }
}
```

## 🚢 Deployment

### Docker Build

```dockerfile
# Multi-stage build
FROM node:18-alpine as build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
```

### Nginx Configuration

The `nginx.conf` file:
- Serves static files from `/usr/share/nginx/html`
- Proxies `/api` requests to backend
- Handles client-side routing with `try_files`

### Environment Variables in Production

Set at build time:
```bash
docker build --build-arg VITE_API_URL=https://api.example.com -t frontend .
```

Or configure nginx to inject at runtime using templates.

## 🎯 User Workflows

### Viewing Issues

1. Dashboard loads and fetches initial data
2. Metrics show overview statistics
3. Issue table displays all issues
4. Use status filter to narrow down
5. Click PR links to view on GitHub

### Triggering a Fix

1. Find issue with status "NEW"
2. Click "Trigger AI Fix" button
3. Button shows "Fixing..." while processing
4. Activity feed shows progress events
5. Issue list refreshes with new status
6. PR link appears when complete

### Monitoring Progress

1. Watch activity feed for real-time updates
2. Check metrics panel for aggregate stats
3. Filter issues by status to see:
   - NEW: Awaiting fix
   - FIXING: Currently processing
   - PR_OPEN: Ready for review
   - CI_PASSED: Succeeded
   - CI_FAILED: Needs attention

### Manual Sync

1. Click "Sync from SonarQube" button
2. Backend fetches latest issues
3. Alert shows number of new issues
4. Issue list refreshes automatically

## 🐛 Troubleshooting

### "Failed to fetch" errors

- Check backend is running: `curl http://localhost:8000/health`
- Verify CORS configuration in backend
- Check browser console for details

### Blank page on load

- Check browser console for errors
- Verify API_BASE_URL is correct
- Ensure backend API is accessible

### Data not updating

- Check polling intervals in config
- Verify network tab shows API calls
- Check backend logs for errors

## 📦 Dependencies

```json
{
  "react": "^18.2.0",           // UI framework
  "react-dom": "^18.2.0",       // React DOM rendering
  "react-router-dom": "^6.21.1", // Routing (future use)
  "typescript": "^5.2.2",       // Type safety
  "vite": "^5.0.8"              // Build tool
}
```

## 🎓 Learning Resources

- [React Documentation](https://react.dev/)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [Vite Guide](https://vitejs.dev/guide/)
- [Fetch API](https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API)

## 🔄 Future Enhancements

Potential improvements for learning:

- [ ] Add React Router for multi-page navigation
- [ ] Implement WebSocket for true real-time updates
- [ ] Add authentication with JWT
- [ ] Create detailed issue view page
- [ ] Add charts/graphs for metrics visualization
- [ ] Implement dark mode toggle
- [ ] Add export functionality (CSV/JSON)
- [ ] Create mobile app version

## 📄 License

MIT - Free to use for learning and projects!
