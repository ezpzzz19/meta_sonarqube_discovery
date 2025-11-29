# Backend - SonarQube Code Janitor

FastAPI backend service that orchestrates the AI-powered code fixing workflow.

## 🏗️ Architecture

The backend is built with FastAPI and follows a clean, modular architecture:

```
app/
├── main.py              # FastAPI app initialization and lifecycle
├── config.py            # Pydantic settings for environment configuration
├── database.py          # SQLAlchemy session management
├── models.py            # Database models (Issue, Event)
├── schemas.py           # Pydantic request/response schemas
├── api.py               # REST API route handlers
├── sonarqube_client.py  # SonarQube API integration
├── github_client.py     # GitHub API integration
├── ai_client.py         # OpenAI API integration
├── fixer_service.py     # Core business logic for fixing issues
└── background.py        # Background polling task
```

## 🚀 Quick Start

### Local Development

1. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**
   ```bash
   cp ../infra/.env.example .env
   # Edit .env with your actual values
   ```

4. **Setup database**
   ```bash
   # Start PostgreSQL (or use docker-compose)
   # Then run migrations
   alembic upgrade head
   ```

5. **Run the server**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

6. **Access the API**
   - Interactive docs: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc
   - Health check: http://localhost:8000/health

## 📡 API Endpoints

### Issues

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/issues` | List issues (paginated, filterable) |
| `GET` | `/api/issues/{id}` | Get issue details with events |
| `POST` | `/api/issues/{id}/trigger-fix` | Manually trigger AI fix |

**Query Parameters for `/api/issues`:**
- `page` (int): Page number (default: 1)
- `page_size` (int): Items per page (default: 50, max: 100)
- `status` (string): Filter by status (NEW, FIXING, PR_OPEN, etc.)
- `severity` (string): Filter by severity (BLOCKER, CRITICAL, MAJOR, etc.)

### Events

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/events/recent` | Get recent events across all issues |

**Query Parameters:**
- `limit` (int): Number of events to return (default: 50, max: 200)

### Metrics

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/metrics/summary` | Get aggregate statistics |

**Response includes:**
- Total issues
- Issues by status (NEW, PR_OPEN, CI_PASSED, etc.)
- Total PRs created
- Success rate (% of issues that passed CI)

### Sync

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/sync` | Manually trigger SonarQube sync |

## 🔧 Configuration

All configuration is done via environment variables using Pydantic Settings.

### Required Variables

```bash
# SonarQube
SONARQUBE_URL=https://your-sonarqube.com
SONARQUBE_TOKEN=your-token
SONARQUBE_PROJECT_KEY=your-project

# GitHub
GITHUB_TOKEN=ghp_your_token
GITHUB_REPO_OWNER=username
GITHUB_REPO_NAME=repo-name

# OpenAI
OPENAI_API_KEY=sk-your-key
```

### Optional Variables

```bash
# GitHub
GITHUB_DEFAULT_BRANCH=main  # Default: main

# OpenAI
OPENAI_MODEL=gpt-4  # Default: gpt-4
# Options: gpt-4, gpt-4-turbo-preview, gpt-3.5-turbo

# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/dbname
# Default: postgresql://postgres:postgres@localhost:5432/sonarqube_codex

# Fixer Service
AUTO_FIX=false  # Default: false (manual mode)
POLL_INTERVAL_SECONDS=60  # Default: 60

# API
CORS_ORIGINS=["http://localhost:3000"]  # Default: includes common dev ports
```

## 🔄 Workflow

### Issue Detection & Fixing

1. **Sync Issues** (Manual or Automatic)
   ```python
   # Called by background poller or /api/sync endpoint
   sonarqube_client.get_issues()
   # Creates new Issue records with status=NEW
   ```

2. **Trigger Fix** (Manual or Automatic)
   ```python
   fixer_service.attempt_fix(issue_id)
   ```

   The fix process:
   1. Update status to `FIXING`
   2. Fetch file content from GitHub
   3. Call OpenAI to generate fix
   4. Create new branch: `ai-fix/{issue_key}`
   5. Commit the fix
   6. Create pull request
   7. Update status to `PR_OPEN`
   8. Log events for each step

3. **Track Events**
   - All major actions create Event records
   - Event types: ISSUE_DETECTED, AI_CALLED, PR_CREATED, ERROR, etc.
   - Visible in the dashboard activity feed

## 🗄️ Database Models

### Issue Model

```python
class Issue(Base):
    id: UUID
    sonarqube_issue_key: str (unique)
    project_key: str
    rule: str
    severity: str
    component: str  # File path
    line: int | None
    message: str | None
    status: IssueStatus
    pr_url: str | None
    pr_branch: str | None
    created_at: datetime
    updated_at: datetime
```

**Status Enum:**
- `NEW`: Issue detected, not yet fixed
- `FIXING`: Fix in progress
- `PR_OPEN`: Pull request created
- `CI_PASSED`: CI checks passed
- `CI_FAILED`: CI checks failed
- `CLOSED`: Issue resolved/closed

### Event Model

```python
class Event(Base):
    id: UUID
    issue_id: UUID (FK)
    event_type: EventType
    message: str
    metadata: str | None  # JSON
    created_at: datetime
```

**Event Types:**
- `ISSUE_DETECTED`: New issue found in SonarQube
- `AI_CALLED`: AI service invoked
- `PR_CREATED`: Pull request created
- `CI_PASSED`: CI checks passed
- `CI_FAILED`: CI checks failed
- `STATUS_UPDATED`: Issue status changed
- `ERROR`: Error occurred

## 🧪 Testing

### Manual Testing

Use the interactive API docs at `/docs` to test endpoints:

1. **Test sync**: `POST /api/sync`
2. **List issues**: `GET /api/issues`
3. **Trigger fix**: `POST /api/issues/{id}/trigger-fix`
4. **View events**: `GET /api/events/recent`

### Database Queries

```bash
# Connect to database
psql postgresql://postgres:postgres@localhost:5432/sonarqube_codex

# View issues
SELECT sonarqube_issue_key, status, pr_url FROM issues;

# View events
SELECT event_type, message, created_at FROM events ORDER BY created_at DESC LIMIT 10;
```

## 🔌 Client Integrations

### SonarQube Client

```python
# Fetch issues from SonarQube
response = await sonarqube_client.get_issues(
    project_key="my-project",
    statuses=["OPEN", "CONFIRMED"],
    page=1,
    page_size=100
)
```

### GitHub Client

```python
# Fetch file content
content, sha = github_client.get_file_content("src/main.py")

# Create branch
github_client.create_branch("ai-fix/issue-123")

# Update file
github_client.update_file(
    file_path="src/main.py",
    content=fixed_content,
    commit_message="Fix issue",
    branch="ai-fix/issue-123",
    sha=sha
)

# Create PR
pr_url = github_client.create_pull_request(
    title="Fix SonarQube issue",
    body="Description",
    head_branch="ai-fix/issue-123"
)
```

### AI Client

```python
# Generate fix
result = await ai_client.generate_fix(
    issue_description="Variable not used",
    rule="python:S1481",
    severity="MAJOR",
    file_path="src/main.py",
    file_content=original_content,
    line_number=42
)

# result = {
#     "success": True,
#     "fixed_content": "...",
#     "explanation": "Removed unused variable..."
# }
```

## 📚 Dependencies

Key dependencies and their purposes:

- **FastAPI**: Modern web framework
- **Uvicorn**: ASGI server
- **SQLAlchemy**: ORM and database toolkit
- **Alembic**: Database migrations
- **Pydantic**: Data validation and settings
- **httpx**: Async HTTP client for SonarQube
- **PyGithub**: GitHub API client
- **OpenAI**: AI code generation

## 🐛 Troubleshooting

### Database Issues

```bash
# Reset database
alembic downgrade base
alembic upgrade head

# Check connection
python -c "from app.database import engine; engine.connect()"
```

### API Client Issues

Enable detailed logging:

```python
# In app/main.py or config
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Background Poller

Check if running:
```bash
# Look for log messages
docker-compose logs backend | grep "background"
```

## 🔐 Security Notes

- Never commit `.env` files
- Use read-only SonarQube tokens if possible
- GitHub token needs `repo` scope (full repository access)
- OpenAI API key should have rate limits configured
- Consider implementing API key rotation

## 📖 Further Reading

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy ORM Tutorial](https://docs.sqlalchemy.org/en/20/tutorial/)
- [Pydantic Settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
- [SonarQube Web API](https://docs.sonarqube.org/latest/extend/web-api/)
- [GitHub REST API](https://docs.github.com/en/rest)
- [OpenAI API Reference](https://platform.openai.com/docs/api-reference)
