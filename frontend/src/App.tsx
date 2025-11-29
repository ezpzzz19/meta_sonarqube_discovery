/**
 * Main App component.
 */

import './App.css';
import { MetricsPanel } from './components/MetricsPanel';
import { ActivityFeed } from './components/ActivityFeed';
import { IssueList } from './components/IssueList';

function App() {
  return (
    <div className="app">
      <header className="header">
        <h1>🤖 SonarQube Code Janitor</h1>
        <p>AI-powered code quality fixer</p>
      </header>
      
      <div className="container">
        <MetricsPanel />
        
        <div className="main-content">
          <IssueList />
          <ActivityFeed />
        </div>
      </div>
    </div>
  );
}

export default App;
