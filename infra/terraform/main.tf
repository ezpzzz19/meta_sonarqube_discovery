# =============================================================================
# Terraform Configuration - SonarQube Code Janitor on Azure
# Cheapest possible deployment using Container Instances
# =============================================================================

terraform {
  required_version = ">= 1.0"
  
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.0"
    }
  }
}

provider "azurerm" {
  features {
    resource_group {
      # Allow deletion of resource groups even when they contain resources
      prevent_deletion_if_contains_resources = false
    }
  }
  
  # Skip automatic registration of all providers (we only need the ones we manually registered)
  skip_provider_registration = true
}

# =============================================================================
# Resource Group
# =============================================================================

resource "azurerm_resource_group" "main" {
  name     = "${var.project_name}-${var.environment}-rg"
  location = var.location

  tags = {
    project     = "sonarqube-codex"
    environment = var.environment
    managedBy   = "terraform"
  }
}

# =============================================================================
# Container Registry (for custom images)
# =============================================================================

resource "azurerm_container_registry" "acr" {
  name                = "${replace(var.project_name, "-", "")}${var.environment}acr"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  sku                 = "Basic" # Cheapest tier
  admin_enabled       = true

  tags = azurerm_resource_group.main.tags
}

# =============================================================================
# PostgreSQL Flexible Server - DEV/TEST Configuration
# Burstable tier (B_Standard_B1ms) is specifically designed for non-production
# workloads with lower cost and appropriate performance for development/testing
# =============================================================================

resource "azurerm_postgresql_flexible_server" "postgres" {
  name                = "${var.project_name}-${var.environment}-postgres"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  version             = "15"
  
  administrator_login    = "sqadmin"
  administrator_password = var.postgres_password

  # Tier-based SKU: Using B_Standard_B2s for dev/test
  # B_Standard_B2s = 2 vCores (burstable), 4 GiB RAM (~$24-36/month)
  # Better performance than B1ms while still cost-effective for dev/test
  sku_name   = "B_Standard_B2s"
  
  # Storage configuration for dev/test
  storage_mb = 32768  # 32 GB (minimum for Flexible Server)
  
  # Backup configuration (minimal for dev/test)
  backup_retention_days        = 7      # Minimum retention
  geo_redundant_backup_enabled = false  # No geo-redundancy for dev/test
  
  # High availability: DISABLED for dev/test (production would enable this)
  # high_availability {
  #   mode = "ZoneRedundant"  # Only enable for production
  # }
  
  # Single availability zone (not zone-redundant) for cost savings
  zone = "1"

  tags = merge(
    azurerm_resource_group.main.tags,
    {
      "tier"        = "dev-test"
      "cost-center" = "development"
      "workload"    = "non-production"
    }
  )
}

# Firewall rule to allow Azure services
resource "azurerm_postgresql_flexible_server_firewall_rule" "azure_services" {
  name             = "AllowAzureServices"
  server_id        = azurerm_postgresql_flexible_server.postgres.id
  start_ip_address = "0.0.0.0"
  end_ip_address   = "0.0.0.0"
}

# Create databases
resource "azurerm_postgresql_flexible_server_database" "sonarqube" {
  name      = "sonarqube"
  server_id = azurerm_postgresql_flexible_server.postgres.id
  charset   = "UTF8"
  collation = "en_US.utf8"
}

resource "azurerm_postgresql_flexible_server_database" "codex" {
  name      = "sonarqube_codex"
  server_id = azurerm_postgresql_flexible_server.postgres.id
  charset   = "UTF8"
  collation = "en_US.utf8"
}

# =============================================================================
# Storage Account for persistent volumes
# =============================================================================

resource "random_string" "storage_suffix" {
  length  = 6
  special = false
  upper   = false
  numeric = true
}

resource "azurerm_storage_account" "storage" {
  name                     = "${replace(var.project_name, "-", "")}${var.environment}st${random_string.storage_suffix.result}"
  resource_group_name      = azurerm_resource_group.main.name
  location                 = azurerm_resource_group.main.location
  account_tier             = "Standard"
  account_replication_type = "LRS" # Cheapest: Locally redundant
  min_tls_version          = "TLS1_2"

  tags = azurerm_resource_group.main.tags
}

resource "azurerm_storage_share" "sonarqube_data" {
  name                 = "sonarqube-data"
  storage_account_name = azurerm_storage_account.storage.name
  quota                = 5 # 5 GB
}

resource "azurerm_storage_share" "sonarqube_extensions" {
  name                 = "sonarqube-extensions"
  storage_account_name = azurerm_storage_account.storage.name
  quota                = 5
}

resource "azurerm_storage_share" "sonarqube_logs" {
  name                 = "sonarqube-logs"
  storage_account_name = azurerm_storage_account.storage.name
  quota                = 5
}

# =============================================================================
# Container Group (All containers in one group to save costs)
# =============================================================================

resource "azurerm_container_group" "containers" {
  name                = "${var.project_name}-${var.environment}-containers"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  os_type             = "Linux"
  restart_policy      = "Always"

  dns_name_label = "${var.project_name}-${var.environment}-app"

  tags = azurerm_resource_group.main.tags

  # SonarQube Container
  container {
    name   = "sonarqube"
    image  = "sonarqube:10.3.0-community"
    cpu    = "2"
    memory = "4"

    ports {
      port     = 9000
      protocol = "TCP"
    }

    environment_variables = {
      SONAR_JDBC_URL                    = "jdbc:postgresql://${azurerm_postgresql_flexible_server.postgres.fqdn}:5432/sonarqube?sslmode=require"
      SONAR_JDBC_USERNAME               = "sqadmin"
      SONAR_ES_BOOTSTRAP_CHECKS_DISABLE = "true"
    }

    secure_environment_variables = {
      SONAR_JDBC_PASSWORD = var.postgres_password
    }

    # REMOVED: sonarqube-data volume
    # Elasticsearch needs fast local storage, not network-mounted Azure Files
    # Using ephemeral storage instead - data will be rebuilt from PostgreSQL if container restarts
    
    volume {
      name                 = "sonarqube-extensions"
      mount_path           = "/opt/sonarqube/extensions"
      storage_account_name = azurerm_storage_account.storage.name
      storage_account_key  = azurerm_storage_account.storage.primary_access_key
      share_name           = azurerm_storage_share.sonarqube_extensions.name
    }

    volume {
      name                 = "sonarqube-logs"
      mount_path           = "/opt/sonarqube/logs"
      storage_account_name = azurerm_storage_account.storage.name
      storage_account_key  = azurerm_storage_account.storage.primary_access_key
      share_name           = azurerm_storage_share.sonarqube_logs.name
    }
  }

  # Backend Container
  container {
    name   = "backend"
    image  = "${azurerm_container_registry.acr.login_server}/sonarqube-codex-backend:latest"
    cpu    = "1"
    memory = "2"

    ports {
      port     = 8000
      protocol = "TCP"
    }

    environment_variables = {
      DATABASE_URL            = "postgresql://sqadmin:${var.postgres_password}@${azurerm_postgresql_flexible_server.postgres.fqdn}:5432/sonarqube_codex?sslmode=require"
      SONARQUBE_URL           = "http://localhost:9000"
      SONARQUBE_PROJECT_KEY   = var.sonarqube_project_key
      GITHUB_REPO_OWNER       = var.github_repo_owner
      GITHUB_REPO_NAME        = var.github_repo_name
      GITHUB_DEFAULT_BRANCH   = var.github_default_branch
      OPENAI_MODEL            = var.openai_model
      AUTO_FIX                = var.auto_fix
      POLL_INTERVAL_SECONDS   = var.poll_interval_seconds
    }

    secure_environment_variables = {
      SONARQUBE_TOKEN = var.sonarqube_token
      GITHUB_TOKEN    = var.github_token
      OPENAI_API_KEY  = var.openai_api_key
    }
  }

  # Frontend Container
  container {
    name   = "frontend"
    image  = "${azurerm_container_registry.acr.login_server}/sonarqube-codex-frontend:latest"
    cpu    = "1"
    memory = "1"

    ports {
      port     = 80
      protocol = "TCP"
    }

    environment_variables = {
      VITE_API_URL = "http://localhost:8000"
    }
  }

  image_registry_credential {
    server   = azurerm_container_registry.acr.login_server
    username = azurerm_container_registry.acr.admin_username
    password = azurerm_container_registry.acr.admin_password
  }

  depends_on = [
    azurerm_postgresql_flexible_server_database.sonarqube,
    azurerm_postgresql_flexible_server_database.codex
  ]
}
