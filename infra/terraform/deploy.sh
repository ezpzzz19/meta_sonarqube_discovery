#!/bin/bash
# =============================================================================
# Terraform Deployment Script for SonarQube Code Janitor on Azure
# =============================================================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}"
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║    SonarQube Code Janitor - Azure Terraform Deployment       ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# =============================================================================
# Configuration
# =============================================================================

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"

cd "$SCRIPT_DIR"

# =============================================================================
# Check Prerequisites
# =============================================================================

echo "📋 Checking prerequisites..."

# Check Terraform
if ! command -v terraform &> /dev/null; then
    echo -e "${RED}❌ Terraform is not installed${NC}"
    echo "Install from: https://www.terraform.io/downloads"
    exit 1
fi

# Check Azure CLI
if ! command -v az &> /dev/null; then
    echo -e "${RED}❌ Azure CLI is not installed${NC}"
    echo "Install from: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
    exit 1
fi

# Check Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed${NC}"
    exit 1
fi

# Check jq
if ! command -v jq &> /dev/null; then
    echo -e "${YELLOW}⚠️  jq is not installed (optional but recommended)${NC}"
    echo "Install with: brew install jq"
fi

# Check Azure login
if ! az account show &> /dev/null; then
    echo -e "${YELLOW}⚠️  Not logged in to Azure${NC}"
    echo "Logging in..."
    az login
fi

echo -e "${GREEN}✅ Prerequisites check passed${NC}"
echo ""

# =============================================================================
# Setup terraform.tfvars
# =============================================================================

if [ ! -f "terraform.tfvars" ]; then
    echo "📝 Creating terraform.tfvars..."
    echo ""
    echo "Please provide the following information:"
    echo ""
    
    read -p "Azure Region [eastus]: " LOCATION
    LOCATION=${LOCATION:-eastus}
    
    read -sp "PostgreSQL Password (min 8 characters): " POSTGRES_PASSWORD
    echo ""
    
    read -sp "GitHub Personal Access Token: " GITHUB_TOKEN
    echo ""
    
    read -sp "OpenAI API Key: " OPENAI_API_KEY
    echo ""
    
    read -p "GitHub Repository Owner [ezpzzz19]: " GITHUB_REPO_OWNER
    GITHUB_REPO_OWNER=${GITHUB_REPO_OWNER:-ezpzzz19}
    
    read -p "GitHub Repository Name [meta_sonarqube_discovery]: " GITHUB_REPO_NAME
    GITHUB_REPO_NAME=${GITHUB_REPO_NAME:-meta_sonarqube_discovery}
    
    cat > terraform.tfvars <<EOF
project_name = "sqcodex"
environment  = "dev"
location     = "$LOCATION"

postgres_password = "$POSTGRES_PASSWORD"

sonarqube_token       = ""
sonarqube_project_key = "my-fancy-project"

github_token         = "$GITHUB_TOKEN"
github_repo_owner    = "$GITHUB_REPO_OWNER"
github_repo_name     = "$GITHUB_REPO_NAME"
github_default_branch = "main"

openai_api_key = "$OPENAI_API_KEY"
openai_model   = "gpt-4"

auto_fix              = "false"
poll_interval_seconds = "60"
EOF
    
    echo -e "${GREEN}✅ terraform.tfvars created${NC}"
else
    echo -e "${YELLOW}⚠️  terraform.tfvars already exists, skipping creation${NC}"
fi

echo ""

# =============================================================================
# Initialize Terraform
# =============================================================================

echo "🔧 Initializing Terraform..."
terraform init
echo -e "${GREEN}✅ Terraform initialized${NC}"
echo ""

# =============================================================================
# Plan Deployment
# =============================================================================

echo "📊 Creating deployment plan..."
terraform plan -out=tfplan
echo ""

read -p "Do you want to proceed with deployment? (yes/no): " CONFIRM
if [ "$CONFIRM" != "yes" ]; then
    echo "Deployment cancelled."
    exit 0
fi

# =============================================================================
# Apply Infrastructure
# =============================================================================

echo ""
echo "🚀 Deploying infrastructure (this may take 10-15 minutes)..."
terraform apply tfplan
echo -e "${GREEN}✅ Infrastructure deployed${NC}"
echo ""

# =============================================================================
# Get outputs
# =============================================================================

ACR_LOGIN_SERVER=$(terraform output -raw container_registry_login_server)
ACR_NAME=$(terraform output -raw container_registry_name)
ACR_USERNAME=$(terraform output -raw container_registry_username)
ACR_PASSWORD=$(terraform output -raw container_registry_password)

echo "📦 Container Registry: $ACR_LOGIN_SERVER"
echo ""

# =============================================================================
# Build and Push Docker Images
# =============================================================================

echo "🐳 Building and pushing Docker images..."
echo ""

# Login to ACR
echo "🔑 Logging in to Container Registry..."
echo "$ACR_PASSWORD" | docker login $ACR_LOGIN_SERVER -u $ACR_USERNAME --password-stdin
echo ""

# Build and push backend
echo "🏗️  Building backend image..."
cd "$PROJECT_ROOT/backend"
docker build --platform linux/amd64 -t $ACR_LOGIN_SERVER/sonarqube-codex-backend:latest .
docker push $ACR_LOGIN_SERVER/sonarqube-codex-backend:latest
echo -e "${GREEN}✅ Backend image pushed${NC}"
echo ""

# Build and push frontend
echo "🏗️  Building frontend image..."
cd "$PROJECT_ROOT/frontend"
docker build --platform linux/amd64 -t $ACR_LOGIN_SERVER/sonarqube-codex-frontend:latest .
docker push $ACR_LOGIN_SERVER/sonarqube-codex-frontend:latest
echo -e "${GREEN}✅ Frontend image pushed${NC}"
echo ""

# =============================================================================
# Restart containers
# =============================================================================

cd "$SCRIPT_DIR"

RESOURCE_GROUP=$(terraform output -raw resource_group_name)
CONTAINER_GROUP_NAME="sqcodex-dev-containers"

echo "🔄 Restarting container group to pull new images..."
az container restart --resource-group $RESOURCE_GROUP --name $CONTAINER_GROUP_NAME --no-wait
echo ""

echo "⏳ Waiting for containers to start (60 seconds)..."
sleep 60
echo ""

# =============================================================================
# Display Summary
# =============================================================================

terraform output deployment_summary

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║              🎉 Deployment Complete! 🎉                       ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${YELLOW}⚠️  Important Next Steps:${NC}"
echo "1. Visit SonarQube and change the admin password"
echo "2. Generate a SonarQube token"
echo "3. Run: ./update-sonarqube-token.sh <your-token>"
echo ""
echo -e "${YELLOW}💡 Tip: Save the terraform.tfstate file securely!${NC}"
echo ""
