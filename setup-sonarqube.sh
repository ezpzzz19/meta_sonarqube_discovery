#!/bin/bash

# SonarQube Local Setup Script
# This script helps you set up SonarQube locally with a project and token

set -e

echo "🔧 SonarQube Local Setup"
echo "========================"
echo ""

# Check if SonarQube is running
echo "📡 Checking if SonarQube is accessible..."
max_retries=30
retry_count=0

while [ $retry_count -lt $max_retries ]; do
    if curl -s -f http://localhost:9000/api/system/status > /dev/null 2>&1; then
        echo "✅ SonarQube is running!"
        break
    else
        retry_count=$((retry_count + 1))
        if [ $retry_count -eq $max_retries ]; then
            echo "❌ SonarQube is not accessible at http://localhost:9000"
            echo "Please ensure SonarQube is running (docker-compose up -d sonarqube)"
            exit 1
        fi
        echo "⏳ Waiting for SonarQube to start... ($retry_count/$max_retries)"
        sleep 5
    fi
done

echo ""
echo "⚙️  SonarQube Configuration"
echo "============================"
echo ""
echo "Default credentials: admin / admin"
echo ""
echo "🔐 Please log in to SonarQube at http://localhost:9000"
echo "   You will be prompted to change the password on first login."
echo ""

# Prompt for credentials
read -p "Enter SonarQube username [admin]: " SONAR_USER
SONAR_USER=${SONAR_USER:-admin}

read -sp "Enter SonarQube password: " SONAR_PASS
echo ""
echo ""

# Test authentication
echo "🔑 Testing authentication..."
AUTH_HEADER=$(echo -n "$SONAR_USER:$SONAR_PASS" | base64)

if ! curl -s -f -H "Authorization: Basic $AUTH_HEADER" \
    http://localhost:9000/api/authentication/validate | grep -q "valid.*true"; then
    echo "❌ Authentication failed. Please check your credentials."
    exit 1
fi

echo "✅ Authentication successful!"
echo ""

# Ask for project details
read -p "Enter project key [my-project]: " PROJECT_KEY
PROJECT_KEY=${PROJECT_KEY:-my-project}

read -p "Enter project name [$PROJECT_KEY]: " PROJECT_NAME
PROJECT_NAME=${PROJECT_NAME:-$PROJECT_KEY}

echo ""
echo "📦 Creating project '$PROJECT_NAME' (key: $PROJECT_KEY)..."

# Create project
CREATE_RESPONSE=$(curl -s -X POST \
    -H "Authorization: Basic $AUTH_HEADER" \
    -d "project=$PROJECT_KEY" \
    -d "name=$PROJECT_NAME" \
    http://localhost:9000/api/projects/create)

if echo "$CREATE_RESPONSE" | grep -q "project"; then
    echo "✅ Project created successfully!"
elif echo "$CREATE_RESPONSE" | grep -q "already exists"; then
    echo "ℹ️  Project already exists, skipping creation."
else
    echo "⚠️  Warning: Unexpected response when creating project"
    echo "$CREATE_RESPONSE"
fi

echo ""
echo "🔑 Generating user token..."

# Generate token
TOKEN_NAME="codex-janitor-$(date +%s)"
TOKEN_RESPONSE=$(curl -s -X POST \
    -H "Authorization: Basic $AUTH_HEADER" \
    -d "name=$TOKEN_NAME" \
    http://localhost:9000/api/user_tokens/generate)

TOKEN=$(echo "$TOKEN_RESPONSE" | grep -o '"token":"[^"]*"' | cut -d'"' -f4)

if [ -z "$TOKEN" ]; then
    echo "❌ Failed to generate token"
    echo "Response: $TOKEN_RESPONSE"
    exit 1
fi

echo "✅ Token generated successfully!"
echo ""

# Update .env file
echo "📝 Updating .env file..."

if [ -f "infra/.env" ]; then
    # Update existing values
    sed -i.bak "s|^SONARQUBE_URL=.*|SONARQUBE_URL=http://sonarqube:9000|" infra/.env
    sed -i.bak "s|^SONARQUBE_TOKEN=.*|SONARQUBE_TOKEN=$TOKEN|" infra/.env
    sed -i.bak "s|^SONARQUBE_PROJECT_KEY=.*|SONARQUBE_PROJECT_KEY=$PROJECT_KEY|" infra/.env
    rm -f infra/.env.bak
    echo "✅ Updated infra/.env"
else
    echo "⚠️  infra/.env not found, creating from template..."
    cp infra/.env.example infra/.env
    sed -i.bak "s|^SONARQUBE_URL=.*|SONARQUBE_URL=http://sonarqube:9000|" infra/.env
    sed -i.bak "s|^SONARQUBE_TOKEN=.*|SONARQUBE_TOKEN=$TOKEN|" infra/.env
    sed -i.bak "s|^SONARQUBE_PROJECT_KEY=.*|SONARQUBE_PROJECT_KEY=$PROJECT_KEY|" infra/.env
    rm -f infra/.env.bak
    echo "✅ Created and updated infra/.env"
fi

echo ""
echo "✨ Setup Complete!"
echo "=================="
echo ""
echo "📊 SonarQube Configuration:"
echo "   URL:         http://localhost:9000"
echo "   Project:     $PROJECT_NAME"
echo "   Project Key: $PROJECT_KEY"
echo "   Token:       $TOKEN"
echo ""
echo "📝 Your .env file has been updated with these settings."
echo ""
echo "🔍 Next Steps:"
echo "   1. Configure your GitHub and OpenAI credentials in infra/.env"
echo "   2. Run a SonarQube analysis on your project"
echo "   3. Start the Code Janitor: ./start.sh"
echo ""
echo "📚 To analyze your project with SonarQube Scanner:"
echo "   sonar-scanner \\"
echo "     -Dsonar.projectKey=$PROJECT_KEY \\"
echo "     -Dsonar.sources=. \\"
echo "     -Dsonar.host.url=http://localhost:9000 \\"
echo "     -Dsonar.login=$TOKEN"
echo ""
