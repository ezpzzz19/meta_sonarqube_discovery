#!/bin/bash
# =============================================================================
# Update SonarQube Token in Azure Deployment (Terraform)
# =============================================================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

if [ -z "$1" ]; then
    echo -e "${RED}❌ Usage: ./update-sonarqube-token.sh <sonarqube-token>${NC}"
    echo ""
    echo "Example:"
    echo "  ./update-sonarqube-token.sh squ_abc123..."
    exit 1
fi

SONARQUBE_TOKEN=$1
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

cd "$SCRIPT_DIR"

# Check if terraform.tfvars exists
if [ ! -f "terraform.tfvars" ]; then
    echo -e "${RED}❌ terraform.tfvars not found${NC}"
    echo "Please run ./deploy.sh first"
    exit 1
fi

echo "🔄 Updating SonarQube token in terraform.tfvars..."

# Update the sonarqube_token line
sed -i.bak "s/sonarqube_token[[:space:]]*=.*/sonarqube_token = \"$SONARQUBE_TOKEN\"/" terraform.tfvars

echo -e "${GREEN}✅ Token updated in terraform.tfvars${NC}"
echo ""

echo "📊 Creating deployment plan..."
terraform plan -out=tfplan
echo ""

read -p "Apply the changes? (yes/no): " CONFIRM
if [ "$CONFIRM" != "yes" ]; then
    echo "Update cancelled."
    exit 0
fi

echo ""
echo "🚀 Applying changes..."
terraform apply tfplan

echo ""
RESOURCE_GROUP=$(terraform output -raw resource_group_name)
CONTAINER_GROUP_NAME="sqcodex-dev-containers"

echo "🔄 Restarting container group..."
az container restart --resource-group $RESOURCE_GROUP --name $CONTAINER_GROUP_NAME

echo ""
echo -e "${GREEN}✅ SonarQube token updated successfully!${NC}"
echo ""
echo "⏳ Wait 1-2 minutes for containers to restart, then test the application."
echo ""
