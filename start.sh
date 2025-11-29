#!/bin/bash

# Quick start script for SonarQube Code Janitor

set -e

echo "🤖 SonarQube Code Janitor - Setup Script"
echo "========================================"
echo ""

# Check if .env exists
if [ ! -f "infra/.env" ]; then
    echo "⚠️  No .env file found!"
    echo "📝 Creating .env from template..."
    cp infra/.env.example infra/.env
    echo "✅ Created infra/.env"
    echo ""
    echo "⚠️  IMPORTANT: Edit infra/.env and fill in your:"
    echo "   - SonarQube URL and token"
    echo "   - GitHub token and repository details"
    echo "   - OpenAI API key"
    echo ""
    echo "Then run this script again."
    exit 1
fi

echo "✅ Found .env file"
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running!"
    echo "Please start Docker and try again."
    exit 1
fi

echo "✅ Docker is running"
echo ""

# Build and start services
echo "🚀 Starting services with Docker Compose..."
cd infra
docker-compose up -d --build

echo ""
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check if services are healthy
echo "🔍 Checking service health..."

# Check backend
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ Backend is healthy"
else
    echo "⚠️  Backend may still be starting..."
fi

# Check frontend
if curl -s http://localhost/ > /dev/null; then
    echo "✅ Frontend is healthy"
else
    echo "⚠️  Frontend may still be starting..."
fi

echo ""
echo "✨ Setup complete!"
echo ""
echo "📊 Access the application:"
echo "   Dashboard:  http://localhost"
echo "   Backend API: http://localhost:8000"
echo "   API Docs:    http://localhost:8000/docs"
echo ""
echo "📝 Next steps:"
echo "   1. Open the dashboard: http://localhost"
echo "   2. Click 'Sync from SonarQube' to fetch issues"
echo "   3. Click 'Trigger AI Fix' on any issue to start fixing"
echo ""
echo "🔍 View logs:"
echo "   docker-compose logs -f"
echo ""
echo "🛑 Stop services:"
echo "   docker-compose down"
echo ""
