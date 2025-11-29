# Infrastructure Setup

This directory contains the Infrastructure as Code (IaC) for the SonarQube Code Janitor system.

## 🏗️ Architecture

The system consists of the following services:

1. **PostgreSQL** - Database for both SonarQube and the Code Janitor backend
2. **SonarQube** - Code quality and security analysis platform
3. **Backend** - FastAPI application that orchestrates the fixing process
4. **Frontend** - React dashboard for monitoring and control

## 🚀 Quick Start

### Option 1: Local SonarQube (Recommended for Testing)

```bash
# Start all services including local SonarQube
cd infra
docker-compose up -d

# Wait for SonarQube to initialize (~2 minutes)
docker-compose logs -f sonarqube

# Run setup script to configure SonarQube
cd ..
chmod +x setup-sonarqube.sh
./setup-sonarqube.sh

# Configure remaining credentials (GitHub, OpenAI)
nano infra/.env

# Restart services to apply configuration
cd infra
docker-compose restart backend
```

### Option 2: Use Existing SonarQube

```bash
# Start only app services (no SonarQube)
cd infra
docker-compose up -d postgres backend frontend

# Configure all credentials including SonarQube
nano .env
```

## 📁 Files

- **docker-compose.yml** - Docker Compose configuration for all services
- **.env** - Environment variables (created from .env.example)
- **.env.example** - Template for environment configuration
- **init-sonarqube-db.sql** - PostgreSQL initialization script

## 🔧 Services

### PostgreSQL

- **Port**: 5432
- **Databases**: 
  - `sonarqube` - For SonarQube data
  - `sonarqube_codex` - For Code Janitor data
- **Credentials**: postgres / postgres (change for production!)

### SonarQube

- **Port**: 9000
- **URL**: http://localhost:9000
- **Default Credentials**: admin / admin
- **Database**: Uses PostgreSQL service
- **Volumes**: 
  - `sonarqube_data` - Analysis data
  - `sonarqube_extensions` - Plugins
  - `sonarqube_logs` - Application logs

### Backend API

- **Port**: 8000
- **Health Check**: http://localhost:8000/health
- **API Docs**: http://localhost:8000/docs
- **Database**: Uses PostgreSQL service

### Frontend

- **Port**: 80
- **URL**: http://localhost
- **Technology**: React + Vite + Nginx

## 🔐 Configuration

### Required Environment Variables

```bash
# SonarQube
SONARQUBE_URL=http://sonarqube:9000  # or your external URL
SONARQUBE_TOKEN=your-token-here
SONARQUBE_PROJECT_KEY=your-project-key

# GitHub
GITHUB_TOKEN=ghp_xxxxx
GITHUB_REPO_OWNER=your-username
GITHUB_REPO_NAME=your-repo
GITHUB_DEFAULT_BRANCH=main

# OpenAI
OPENAI_API_KEY=sk-xxxxx
OPENAI_MODEL=gpt-4

# Optional
AUTO_FIX=false  # Enable automatic fixing
POLL_INTERVAL_SECONDS=60  # How often to check for new issues
```

### Service URLs

- **From Host Machine**:
  - SonarQube: `http://localhost:9000`
  - Backend: `http://localhost:8000`
  - Frontend: `http://localhost`

- **From Backend Container** (for SONARQUBE_URL):
  - SonarQube: `http://sonarqube:9000`
  - PostgreSQL: `postgresql://postgres:postgres@postgres:5432/sonarqube_codex`

## 📋 Common Commands

```bash
# Start all services
docker-compose up -d

# Start specific service
docker-compose up -d sonarqube

# View logs
docker-compose logs -f
docker-compose logs -f backend

# Restart a service
docker-compose restart backend

# Stop all services
docker-compose down

# Stop and remove volumes (DELETES DATA!)
docker-compose down -v

# Rebuild after code changes
docker-compose up -d --build

# Check service status
docker-compose ps

# Execute command in container
docker-compose exec backend bash
docker-compose exec postgres psql -U postgres
```

## 🔍 Troubleshooting

### SonarQube won't start

```bash
# Check logs
docker-compose logs sonarqube

# Ensure enough memory (SonarQube needs ~2GB RAM)
docker stats

# On macOS/Linux, check vm.max_map_count
sysctl vm.max_map_count
# Should be at least 262144
sudo sysctl -w vm.max_map_count=262144
```

### "Connection refused" errors

```bash
# Check if services are healthy
docker-compose ps

# Check network connectivity
docker-compose exec backend ping sonarqube
docker-compose exec backend ping postgres

# Verify environment variables
docker-compose exec backend env | grep SONARQUBE
```

### Database connection issues

```bash
# Check PostgreSQL logs
docker-compose logs postgres

# Connect to database manually
docker-compose exec postgres psql -U postgres -d sonarqube_codex

# List databases
docker-compose exec postgres psql -U postgres -c "\l"
```

### Port already in use

```bash
# Check what's using the port
lsof -i :9000  # SonarQube
lsof -i :8000  # Backend
lsof -i :80    # Frontend
lsof -i :5432  # PostgreSQL

# Change ports in docker-compose.yml if needed
```

## 🔄 Development Workflow

### Making Backend Changes

```bash
# Changes are hot-reloaded via volume mount
cd infra
docker-compose restart backend
```

### Making Frontend Changes

```bash
# Rebuild frontend
cd infra
docker-compose up -d --build frontend
```

### Database Migrations

```bash
# Run migrations
docker-compose exec backend alembic upgrade head

# Create new migration
docker-compose exec backend alembic revision --autogenerate -m "description"
```

## 📊 Monitoring

### Health Checks

```bash
# Backend health
curl http://localhost:8000/health

# SonarQube status
curl http://localhost:9000/api/system/status

# PostgreSQL
docker-compose exec postgres pg_isready
```

### Resource Usage

```bash
# View resource usage
docker stats

# View disk usage
docker system df
```

## 🔒 Security Notes

⚠️ **This configuration is for development/testing only!**

For production:
- Change default PostgreSQL passwords
- Use secrets management (Docker secrets, vault, etc.)
- Enable HTTPS/TLS
- Use proper authentication
- Implement network isolation
- Regular backups
- Update container images regularly

## 🧹 Cleanup

```bash
# Remove containers and networks (keeps volumes)
docker-compose down

# Remove everything including data
docker-compose down -v

# Remove unused Docker resources
docker system prune -a
```

## 📚 Additional Resources

- [SonarQube Documentation](https://docs.sonarqube.org/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
