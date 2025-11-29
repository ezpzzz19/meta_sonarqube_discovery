# 🤖 SonarQube Code Janitor

An AI-powered platform that automatically detects and fixes SonarQube code quality issues by generating pull requests with AI-suggested fixes.

## 📋 Overview

This project demonstrates an automated code quality improvement workflow:

1. **Detect**: Monitors SonarQube for code quality issues
2. **Analyze**: Fetches the problematic code from GitHub
3. **Fix**: Uses OpenAI GPT-4 to generate fixes
4. **Submit**: Creates pull requests with the AI-generated fixes
5. **Track**: Provides a dashboard to monitor the entire process

Perfect for student projects, demos, or exploring AI-assisted development workflows.

## 🏗️ Architecture

```
┌─────────────────┐
│   SonarQube     │  (External - monitors code quality)
└────────┬────────┘
         │
         ▼
┌─────────────────┐      ┌──────────────┐      ┌─────────────┐
│  FastAPI Backend│─────▶│  PostgreSQL  │      │   OpenAI    │
│  (Python 3.11)  │◀─────│   Database   │      │   GPT-4     │
└────────┬────────┘      └──────────────┘      └──────┬──────┘
         │                                             │
         │  ┌──────────────────────────────────────────┘
         │  │
         ▼  ▼
┌─────────────────┐      ┌──────────────┐
│  GitHub API     │      │   React UI   │
│  (source + PRs) │      │  Dashboard   │
└─────────────────┘      └──────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- SonarQube instance (URL + authentication token)
- GitHub repository (with a personal access token)
- OpenAI API key

### Setup

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd sonarqube_codex
   ```

2. **Configure environment variables**
   ```bash
   cd infra
   cp .env.example .env
   # Edit .env and fill in your actual values
   ```

3. **Start the services**
   ```bash
   docker-compose up -d
   ```

4. **Access the dashboard**
   - Frontend: http://localhost
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### First Run

1. Click "Sync from SonarQube" in the dashboard to fetch issues
2. Click "Trigger AI Fix" on any issue to generate a fix
3. The system will create a pull request on GitHub automatically
4. Monitor the activity feed for real-time updates

## 📁 Project Structure

```
sonarqube_codex/
├── backend/              # FastAPI backend service
│   ├── app/
│   │   ├── main.py      # Application entry point
│   │   ├── config.py    # Configuration management
│   │   ├── models.py    # Database models
│   │   ├── schemas.py   # Pydantic schemas
│   │   ├── database.py  # Database session handling
│   │   ├── api.py       # REST API endpoints
│   │   ├── sonarqube_client.py  # SonarQube integration
│   │   ├── github_client.py     # GitHub integration
│   │   ├── ai_client.py         # OpenAI integration
│   │   ├── fixer_service.py     # Core fix orchestration
│   │   └── background.py        # Background polling
│   ├── alembic/         # Database migrations
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/            # React TypeScript frontend
│   ├── src/
│   │   ├── components/  # React components
│   │   ├── api.ts       # API client
│   │   ├── types.ts     # TypeScript types
│   │   ├── config.ts    # Frontend config
│   │   └── main.tsx     # Entry point
│   ├── package.json
│   └── Dockerfile
│
├── infra/               # Infrastructure
│   ├── docker-compose.yml
│   └── .env.example
│
└── README.md
```

## 🔧 Configuration

### Backend Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `SONARQUBE_URL` | SonarQube instance URL | ✅ | - |
| `SONARQUBE_TOKEN` | SonarQube auth token | ✅ | - |
| `SONARQUBE_PROJECT_KEY` | Project to monitor | ✅ | - |
| `GITHUB_TOKEN` | GitHub personal access token | ✅ | - |
| `GITHUB_REPO_OWNER` | Repository owner | ✅ | - |
| `GITHUB_REPO_NAME` | Repository name | ✅ | - |
| `GITHUB_DEFAULT_BRANCH` | Default branch | ❌ | `main` |
| `OPENAI_API_KEY` | OpenAI API key | ✅ | - |
| `OPENAI_MODEL` | Model to use | ❌ | `gpt-4` |
| `AUTO_FIX` | Auto-fix new issues | ❌ | `false` |
| `POLL_INTERVAL_SECONDS` | Polling frequency | ❌ | `60` |
| `DATABASE_URL` | PostgreSQL URL | ❌ | (set by docker) |

### Auto vs Manual Mode

- **Manual Mode** (`AUTO_FIX=false`): Issues are synced but fixes must be triggered via the dashboard
- **Auto Mode** (`AUTO_FIX=true`): New issues are automatically fixed in the background

## 🎯 Features

### Dashboard Features

- **Metrics Panel**: Real-time statistics on issues and fixes
- **Issue List**: Filterable table of all SonarQube issues
  - Status filtering (NEW, FIXING, PR_OPEN, CI_PASSED, etc.)
  - Manual fix triggering
  - Direct links to SonarQube and GitHub PRs
- **Activity Feed**: Live event stream showing:
  - Issue detection
  - AI fix attempts
  - PR creation
  - CI status updates

### Backend Features

- **REST API** with FastAPI
- **Database persistence** with PostgreSQL and SQLAlchemy
- **Background polling** for automatic issue detection
- **Event tracking** for complete audit trail
- **Error handling** and retry logic

## 🔌 API Endpoints

### Issues

- `GET /api/issues` - List all issues (paginated, filterable)
- `GET /api/issues/{id}` - Get issue details with events
- `POST /api/issues/{id}/trigger-fix` - Manually trigger fix

### Events

- `GET /api/events/recent` - Get recent events

### Metrics

- `GET /api/metrics/summary` - Get aggregate statistics

### Sync

- `POST /api/sync` - Manually sync issues from SonarQube

### Documentation

- `GET /docs` - Interactive API documentation (Swagger UI)
- `GET /health` - Health check endpoint

## 🗄️ Database Schema

### Issues Table

```sql
- id (UUID, PK)
- sonarqube_issue_key (unique)
- project_key
- rule
- severity
- component (file path)
- line
- message
- status (enum: NEW, FIXING, PR_OPEN, CI_PASSED, CI_FAILED, CLOSED)
- pr_url
- pr_branch
- created_at
- updated_at
```

### Events Table

```sql
- id (UUID, PK)
- issue_id (FK → issues)
- event_type (enum: ISSUE_DETECTED, AI_CALLED, PR_CREATED, etc.)
- message
- metadata
- created_at
```

## 🧪 Development

### Running Locally (Without Docker)

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp ../infra/.env.example .env  # Edit with your values
alembic upgrade head
uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

### Database Migrations

```bash
cd backend
# Create a new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

## 🐛 Troubleshooting

### Common Issues

1. **"Failed to fetch file from GitHub"**
   - Verify `GITHUB_TOKEN` has repo permissions
   - Check that `GITHUB_REPO_OWNER` and `GITHUB_REPO_NAME` are correct
   - Ensure the file path exists in the repository

2. **"Failed to connect to SonarQube"**
   - Verify `SONARQUBE_URL` is accessible from the backend container
   - Check `SONARQUBE_TOKEN` is valid
   - Ensure `SONARQUBE_PROJECT_KEY` exists

3. **"AI failed to generate fix"**
   - Verify `OPENAI_API_KEY` is valid
   - Check OpenAI API quota/limits
   - Review the error message in the activity feed

4. **Database connection errors**
   - Wait for PostgreSQL to be fully initialized (check with `docker-compose logs postgres`)
   - Verify `DATABASE_URL` format

### Viewing Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f postgres
```

## 🔐 Security Considerations

⚠️ **This is a demo/student project. For production use:**

- Store secrets in a secure vault (e.g., AWS Secrets Manager, HashiCorp Vault)
- Use HTTPS for all external communications
- Implement rate limiting on API endpoints
- Add authentication/authorization to the dashboard
- Review and approve AI-generated fixes before merging
- Implement proper error handling and logging
- Use a dedicated service account with minimal permissions

## 📚 Technologies Used

- **Backend**: Python 3.11, FastAPI, SQLAlchemy, Alembic, Pydantic
- **Frontend**: React 18, TypeScript, Vite
- **Database**: PostgreSQL 15
- **AI**: OpenAI GPT-4
- **Integrations**: SonarQube REST API, GitHub API (PyGithub)
- **Infrastructure**: Docker, Docker Compose

## 🤝 Contributing

This is a student/demo project, but contributions are welcome!

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

MIT License - feel free to use this for learning and experimentation.

## 🙏 Acknowledgments

- Built as a demonstration of AI-assisted development workflows
- Inspired by the need for automated code quality improvements
- Uses OpenAI's GPT-4 for intelligent code generation

## 📞 Support

For issues or questions:
- Check the troubleshooting section above
- Review the API documentation at `/docs`
- Check Docker logs for error details

---

**Note**: This project is designed for educational and demonstration purposes. Always review AI-generated code changes before merging them into production codebases.
