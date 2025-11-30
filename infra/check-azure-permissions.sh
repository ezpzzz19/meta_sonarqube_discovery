#!/bin/bash
# =============================================================================
# Check Azure Permissions - SonarQube Code Janitor
# =============================================================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}"
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║         Azure Permissions Checker                             ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Check if logged in
if ! az account show &> /dev/null; then
    echo -e "${RED}❌ Not logged in to Azure${NC}"
    echo "Run: az login"
    exit 1
fi

echo -e "${GREEN}✅ Logged in as: $(az account show --query user.name -o tsv)${NC}"
echo -e "${GREEN}✅ Subscription: $(az account show --query name -o tsv)${NC}"
echo -e "   Subscription ID: $(az account show --query id -o tsv)"
echo ""

# Check role assignments
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 Your Role Assignments"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
az role assignment list \
  --assignee $(az account show --query user.name -o tsv) \
  --query "[].{Role:roleDefinitionName, Scope:scope}" \
  --output table

# Check if has Contributor role
HAS_CONTRIBUTOR=$(az role assignment list \
  --assignee $(az account show --query user.name -o tsv) \
  --query "[?roleDefinitionName=='Contributor'] | length(@)")

if [ "$HAS_CONTRIBUTOR" -gt 0 ]; then
    echo -e "${GREEN}✅ You have Contributor role - deployment should work!${NC}"
else
    echo -e "${YELLOW}⚠️  No Contributor role found${NC}"
    echo "   You may need to request Contributor access from your Azure admin"
fi

echo ""

# Check resource providers
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📦 Resource Provider Registration Status"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

REQUIRED_PROVIDERS=(
  "Microsoft.ContainerInstance"
  "Microsoft.ContainerRegistry"
  "Microsoft.DBforPostgreSQL"
  "Microsoft.Storage"
)

ALL_REGISTERED=true

for provider in "${REQUIRED_PROVIDERS[@]}"; do
  status=$(az provider show --namespace $provider --query "registrationState" -o tsv 2>/dev/null || echo "Unknown")
  if [ "$status" = "Registered" ]; then
    echo -e "  ${GREEN}✅ $provider${NC}"
  else
    echo -e "  ${RED}❌ $provider${NC} (Status: $status)"
    echo -e "     ${YELLOW}Register with: az provider register --namespace $provider${NC}"
    ALL_REGISTERED=false
  fi
done

echo ""

# Check quota
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 Quota Check (East US region)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Container Instances need 4 vCPUs total (2 for SonarQube, 1 for backend, 1 for frontend)
VCPU_INFO=$(az vm list-usage --location eastus --query "[?localName=='Total Regional vCPUs']" 2>/dev/null)

if [ ! -z "$VCPU_INFO" ]; then
    CURRENT=$(echo $VCPU_INFO | jq -r '.[0].currentValue')
    LIMIT=$(echo $VCPU_INFO | jq -r '.[0].limit')
    AVAILABLE=$((LIMIT - CURRENT))
    
    echo "   Current vCPU usage: $CURRENT / $LIMIT"
    echo "   Available vCPUs: $AVAILABLE"
    
    if [ $AVAILABLE -ge 4 ]; then
        echo -e "   ${GREEN}✅ Sufficient quota (need 4 vCPUs, have $AVAILABLE available)${NC}"
    else
        echo -e "   ${YELLOW}⚠️  May not have enough quota (need 4 vCPUs, have $AVAILABLE available)${NC}"
        echo "   Request quota increase if deployment fails"
    fi
else
    echo -e "   ${YELLOW}⚠️  Could not check quota (jq may not be installed)${NC}"
fi

echo ""

# Check if can create resource group
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🧪 Permission Tests"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

TEST_RG_NAME="test-permissions-$(date +%s)"

echo -n "Testing resource group creation... "
if az group create --name $TEST_RG_NAME --location eastus &> /dev/null; then
    echo -e "${GREEN}✅ Success${NC}"
    az group delete --name $TEST_RG_NAME --yes --no-wait &> /dev/null
else
    echo -e "${RED}❌ Failed${NC}"
    echo -e "   ${YELLOW}You may not have permission to create resource groups${NC}"
fi

echo -n "Testing container registry name availability... "
if az acr check-name --name testacr$(date +%s) &> /dev/null; then
    echo -e "${GREEN}✅ Success${NC}"
else
    echo -e "${YELLOW}⚠️  Check failed (may be OK)${NC}"
fi

echo ""

# Summary
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 Summary"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ "$HAS_CONTRIBUTOR" -gt 0 ] && [ "$ALL_REGISTERED" = true ]; then
    echo -e "${GREEN}✅ Ready to deploy!${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. cd infra/terraform"
    echo "  2. ./deploy.sh"
else
    echo -e "${YELLOW}⚠️  Action required before deployment:${NC}"
    if [ "$HAS_CONTRIBUTOR" -eq 0 ]; then
        echo "   - Request Contributor role from your Azure admin"
    fi
    if [ "$ALL_REGISTERED" = false ]; then
        echo "   - Register required resource providers (see above)"
    fi
fi

echo ""
echo "For detailed permission information, see: AZURE_PERMISSIONS.md"
echo ""
