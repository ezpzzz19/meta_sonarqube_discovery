#!/bin/bash

# System Status Check Script
# Quickly check the health of all services

echo "🔍 SonarQube Code Janitor - System Status"
echo "========================================="
echo ""

# Check Docker
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running!"
    exit 1
fi

echo "✅ Docker is running"
echo ""

# Check if services are running
cd infra 2>/dev/null || cd "$(dirname "$0")/infra"

echo "📊 Service Status:"
echo ""

# PostgreSQL
if docker-compose ps postgres | grep -q "Up"; then
    if docker-compose exec -T postgres pg_isready > /dev/null 2>&1; then
        echo "✅ PostgreSQL - Healthy"
    else
        echo "⚠️  PostgreSQL - Running but not ready"
    fi
else
    echo "❌ PostgreSQL - Not running"
fi

# SonarQube
if docker-compose ps sonarqube | grep -q "Up"; then
    STATUS=$(curl -s http://localhost:9000/api/system/status 2>/dev/null | grep -o '"status":"[^"]*"' | cut -d'"' -f4)
    if [ "$STATUS" = "UP" ]; then
        echo "✅ SonarQube - Operational (http://localhost:9000)"
    elif [ "$STATUS" = "STARTING" ]; then
        echo "🟡 SonarQube - Starting... (wait 1-2 minutes)"
    else
        echo "⚠️  SonarQube - Status: ${STATUS:-Unknown}"
    fi
else
    echo "❌ SonarQube - Not running"
fi

# Backend
if docker-compose ps backend | grep -q "Up"; then
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ Backend API - Healthy (http://localhost:8000)"
    else
        echo "⚠️  Backend API - Running but not responding"
    fi
else
    echo "❌ Backend API - Not running"
fi

# Frontend
if docker-compose ps frontend | grep -q "Up"; then
    if curl -s -o /dev/null -w "%{http_code}" http://localhost/ 2>/dev/null | grep -q "200"; then
        echo "✅ Frontend - Healthy (http://localhost)"
    else
        echo "⚠️  Frontend - Running but not responding"
    fi
else
    echo "❌ Frontend - Not running"
fi

echo ""
echo "🌐 Access Points:"
echo "   Frontend:    http://localhost"
echo "   Backend API: http://localhost:8000/docs"
echo "   SonarQube:   http://localhost:9000"
echo ""

# Check .env configuration
if [ -f "infra/.env" ] || [ -f ".env" ]; then
    ENV_FILE="infra/.env"
    [ -f ".env" ] && ENV_FILE=".env"
    
    echo "⚙️  Configuration Status:"
    
    # Check each required config
    if grep -q "SONARQUBE_TOKEN=your-sonarqube-token-here" "$ENV_FILE" 2>/dev/null; then
        echo "   ⚠️  SonarQube token not configured"
    else
        echo "   ✅ SonarQube configured"
    fi
    
    if grep -q "GITHUB_TOKEN=your-github-token-here" "$ENV_FILE" 2>/dev/null; then
        echo "   ⚠️  GitHub token not configured"
    else
        echo "   ✅ GitHub configured"
    fi
    
    if grep -q "OPENAI_API_KEY=your-openai-api-key-here" "$ENV_FILE" 2>/dev/null; then
        echo "   ⚠️  OpenAI API key not configured"
    else
        echo "   ✅ OpenAI configured"
    fi
else
    echo "⚠️  No .env file found"
fi

echo ""
echo "📋 Quick Actions:"
echo "   View logs:           docker-compose logs -f"
echo "   Restart service:     docker-compose restart <service>"
echo "   Stop all:            docker-compose down"
echo "   Configure SonarQube: ./setup-sonarqube.sh"
echo ""
