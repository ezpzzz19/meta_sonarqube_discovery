# 🚀 Quick Start Guide

Get the SonarQube Code Janitor running in 5 minutes!

## Prerequisites

Before you begin, ensure you have:

- ✅ Docker and Docker Compose installed
- ✅ **Option A: Local SonarQube** (recommended for testing)
  - Included in the docker-compose setup - see "Local SonarQube Setup" below
- ✅ **Option B: Existing SonarQube instance**
  - URL (e.g., `https://sonarqube.example.com`)
  - Authentication token (generate at: SonarQube > My Account > Security)
  - Project key to monitor
- ✅ GitHub Personal Access Token with `repo` scope
  - Generate at: GitHub > Settings > Developer settings > Personal access tokens
- ✅ OpenAI API key
  - Get from: https://platform.openai.com/api-keys

---

## 🏠 Local SonarQube Setup (Recommended for Testing)

If you don't have a SonarQube instance, we provide a complete local setup!

### Step 1: Start SonarQube

```bash
cd infra
docker-compose up -d sonarqube postgres
```

Wait for SonarQube to start (takes ~2 minutes):

```bash
# Check logs
docker-compose logs -f sonarqube

# Wait until you see: "SonarQube is operational"
```

### Step 2: Configure SonarQube

Access SonarQube at **http://localhost:9000**

- Default credentials: `admin` / `admin`
- You'll be prompted to change the password on first login

### Step 3: Run Setup Script

```bash
# From project root
chmod +x setup-sonarqube.sh
./setup-sonarqube.sh
```

This script will:
- ✅ Create a project in SonarQube
- ✅ Generate an authentication token
- ✅ Update your `.env` file automatically

### Step 4: Analyze Your Project

Run SonarQube analysis on your codebase:

```bash
# Install sonar-scanner (if not already installed)
# macOS: brew install sonar-scanner
# Linux: Download from https://docs.sonarqube.org/latest/analysis/scan/sonarscanner/

# Run analysis (use values from setup script output)
sonar-scanner \
  -Dsonar.projectKey=my-project \
  -Dsonar.sources=. \
  -Dsonar.host.url=http://localhost:9000 \
  -Dsonar.login=YOUR_TOKEN_FROM_SETUP
```

Now continue to "Step 2: Configure Environment" below (GitHub and OpenAI only).

---

## Step 1: Clone & Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd sonarqube_codex

# Make start script executable
chmod +x start.sh
```

## Step 2: Configure Environment

```bash
# Copy environment template
cd infra
cp .env.example .env

# Edit .env file with your credentials
nano .env  # or use your preferred editor
```

**Required values to set in `.env`:**

```bash
# SonarQube
SONARQUBE_URL=https://your-sonarqube-instance.com
SONARQUBE_TOKEN=squ_abc123...
SONARQUBE_PROJECT_KEY=my-project-key

# GitHub
GITHUB_TOKEN=ghp_abc123...
GITHUB_REPO_OWNER=your-username
GITHUB_REPO_NAME=your-repo-name

# OpenAI
OPENAI_API_KEY=sk-abc123...
```

## Step 3: Start the Application

```bash
# From project root
./start.sh
```

Or manually:

```bash
cd infra
docker-compose up -d
```

## Step 4: Access the Dashboard

Open your browser to:
- **Dashboard**: http://localhost
- **API Docs**: http://localhost:8000/docs

## Step 5: Use the Application

1. **Sync Issues**
   - Click "Sync from SonarQube" button in the dashboard
   - Wait for issues to be imported

2. **Trigger a Fix**
   - Find an issue with status "NEW"
   - Click "Trigger AI Fix"
   - Watch the activity feed for progress

3. **Monitor Progress**
   - View metrics panel for statistics
   - Check activity feed for real-time events
   - Click PR links to review generated fixes

## Common Commands

```bash
# View logs
cd infra
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f postgres

# Stop services
docker-compose down

# Restart a service
docker-compose restart backend

# Rebuild after code changes
docker-compose up -d --build
```

## Manual vs Auto Mode

### Manual Mode (Default)

```bash
AUTO_FIX=false
```

- Issues are detected but not automatically fixed
- You trigger fixes manually via the dashboard
- **Recommended for learning and testing**

### Auto Mode

```bash
AUTO_FIX=true
```

- New issues are automatically fixed
- Background service polls every 60 seconds (configurable)
- **Use with caution** - reviews AI fixes before merging!

## Troubleshooting

### Services won't start

```bash
# Check Docker is running
docker info

# Check if ports are available
lsof -i :80    # Frontend
lsof -i :8000  # Backend
lsof -i :5432  # PostgreSQL
```

### "Failed to fetch file from GitHub"

- Verify `GITHUB_TOKEN` has `repo` scope
- Check repository owner and name are correct
- Ensure file exists in the repository

### "Failed to connect to SonarQube"

- Verify SonarQube URL is accessible
- Check authentication token is valid
- Confirm project key exists

### Database connection errors

```bash
# Wait for PostgreSQL to initialize
docker-compose logs postgres

# Reset database
docker-compose down -v
docker-compose up -d
```

## Next Steps

1. **Explore the API**
   - Visit http://localhost:8000/docs
   - Try the interactive endpoints

2. **Review Generated Fixes**
   - Check the pull requests created by the AI
   - Verify the fixes are correct before merging

3. **Customize Configuration**
   - Adjust `POLL_INTERVAL_SECONDS`
   - Change `OPENAI_MODEL` (gpt-4, gpt-3.5-turbo)
   - Configure `AUTO_FIX` mode

4. **Monitor & Learn**
   - Watch the activity feed
   - Study the AI-generated fixes
   - Learn patterns for code quality improvements

## Security Reminders

⚠️ **Important:**

- Never commit `.env` files to version control
- Review AI-generated code before merging
- Use minimal permissions for tokens
- This is a demo - enhance security for production use

## Need Help?

- Check the main README.md for detailed documentation
- Review backend/README.md for API details
- See frontend/README.md for dashboard information
- View logs for error details: `docker-compose logs -f`

## Success Checklist

- [ ] Docker and Docker Compose installed
- [ ] `.env` file created with all required values
- [ ] Services started successfully
- [ ] Dashboard accessible at http://localhost
- [ ] API docs accessible at http://localhost:8000/docs
- [ ] Successfully synced issues from SonarQube
- [ ] Successfully triggered an AI fix
- [ ] Pull request created on GitHub

---

🎉 **Congratulations!** Your AI Code Janitor is now running!
