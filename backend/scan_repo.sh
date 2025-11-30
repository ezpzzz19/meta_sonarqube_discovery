#!/bin/bash
# SonarQube Scanner Script
# This script clones a repository and runs SonarQube analysis

set -e

# Required environment variables
: "${GITHUB_TOKEN:?GITHUB_TOKEN is required}"
: "${GITHUB_REPO_OWNER:?GITHUB_REPO_OWNER is required}"
: "${GITHUB_REPO_NAME:?GITHUB_REPO_NAME is required}"
: "${SONARQUBE_URL:?SONARQUBE_URL is required}"
: "${SONARQUBE_TOKEN:?SONARQUBE_TOKEN is required}"
: "${SONARQUBE_PROJECT_KEY:?SONARQUBE_PROJECT_KEY is required}"

# Optional variables
GITHUB_BRANCH="${GITHUB_DEFAULT_BRANCH:-main}"
WORK_DIR="/tmp/scan-workspace"

echo "🔍 Starting SonarQube Analysis"
echo "================================"
echo "Repository: ${GITHUB_REPO_OWNER}/${GITHUB_REPO_NAME}"
echo "Branch: ${GITHUB_BRANCH}"
echo "Project Key: ${SONARQUBE_PROJECT_KEY}"
echo ""

# Clean workspace
echo "🧹 Cleaning workspace..."
rm -rf "$WORK_DIR"
mkdir -p "$WORK_DIR"
cd "$WORK_DIR"

# Clone repository
echo "📥 Cloning repository..."
REPO_URL="https://${GITHUB_TOKEN}@github.com/${GITHUB_REPO_OWNER}/${GITHUB_REPO_NAME}.git"
git clone --depth 1 --branch "$GITHUB_BRANCH" "$REPO_URL" repo
cd repo

# Run SonarQube Scanner
echo "🔎 Running SonarQube analysis..."
sonar-scanner \
  -Dsonar.projectKey="$SONARQUBE_PROJECT_KEY" \
  -Dsonar.sources=. \
  -Dsonar.host.url="$SONARQUBE_URL" \
  -Dsonar.login="$SONARQUBE_TOKEN" \
  -Dsonar.scm.disabled=true

echo ""
echo "✅ Analysis complete!"
echo "📊 View results at: ${SONARQUBE_URL}/dashboard?id=${SONARQUBE_PROJECT_KEY}"
echo ""

# Cleanup
cd /
rm -rf "$WORK_DIR"
