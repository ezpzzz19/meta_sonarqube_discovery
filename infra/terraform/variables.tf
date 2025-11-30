# =============================================================================
# Variables - SonarQube Code Janitor Terraform Configuration
# =============================================================================

variable "project_name" {
  description = "Name of the project (lowercase, no spaces)"
  type        = string
  default     = "sqcodex"

  validation {
    condition     = can(regex("^[a-z0-9-]{3,15}$", var.project_name))
    error_message = "Project name must be 3-15 characters, lowercase letters, numbers, and hyphens only."
  }
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "dev"

  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be dev, staging, or prod."
  }
}

variable "location" {
  description = "Azure region for resources"
  type        = string
  default     = "eastus"
}

# =============================================================================
# Database Configuration
# =============================================================================

variable "postgres_password" {
  description = "PostgreSQL administrator password"
  type        = string
  sensitive   = true

  validation {
    condition     = length(var.postgres_password) >= 8
    error_message = "Password must be at least 8 characters long."
  }
}

variable "postgres_tier" {
  description = "PostgreSQL pricing tier (burstable for dev/test, general-purpose or memory-optimized for production)"
  type        = string
  default     = "burstable"

  validation {
    condition     = contains(["burstable", "general-purpose", "memory-optimized"], var.postgres_tier)
    error_message = "Tier must be burstable (dev/test), general-purpose, or memory-optimized (production)."
  }
}

variable "postgres_sku" {
  description = "PostgreSQL SKU based on tier. Defaults to cheapest option per tier."
  type        = string
  default     = "B_Standard_B1ms"  # Burstable: 1 vCore, 2 GiB RAM (~$12-18/month)
  
  # Other options:
  # Burstable: B_Standard_B1ms (1 vCore), B_Standard_B2s (2 vCore)
  # General Purpose: GP_Standard_D2s_v3 (2 vCore), GP_Standard_D4s_v3 (4 vCore)
  # Memory Optimized: MO_Standard_E2s_v3 (2 vCore), MO_Standard_E4s_v3 (4 vCore)
}

# =============================================================================
# SonarQube Configuration
# =============================================================================

variable "sonarqube_token" {
  description = "SonarQube authentication token (generated after deployment)"
  type        = string
  sensitive   = true
  default     = ""
}

variable "sonarqube_project_key" {
  description = "SonarQube project key to monitor"
  type        = string
  default     = "my-fancy-project"
}

# =============================================================================
# GitHub Configuration
# =============================================================================

variable "github_token" {
  description = "GitHub Personal Access Token with repo permissions"
  type        = string
  sensitive   = true
}

variable "github_repo_owner" {
  description = "GitHub repository owner (username or organization)"
  type        = string
}

variable "github_repo_name" {
  description = "GitHub repository name"
  type        = string
}

variable "github_default_branch" {
  description = "Default branch to create PRs against"
  type        = string
  default     = "main"
}

# =============================================================================
# OpenAI Configuration
# =============================================================================

variable "openai_api_key" {
  description = "OpenAI API key for code generation"
  type        = string
  sensitive   = true
}

variable "openai_model" {
  description = "OpenAI model to use"
  type        = string
  default     = "gpt-4"

  validation {
    condition     = contains(["gpt-4", "gpt-4-turbo-preview", "gpt-3.5-turbo"], var.openai_model)
    error_message = "Model must be gpt-4, gpt-4-turbo-preview, or gpt-3.5-turbo."
  }
}

# =============================================================================
# Application Configuration
# =============================================================================

variable "auto_fix" {
  description = "Enable automatic fixing of new issues"
  type        = string
  default     = "false"

  validation {
    condition     = contains(["true", "false"], var.auto_fix)
    error_message = "auto_fix must be 'true' or 'false'."
  }
}

variable "poll_interval_seconds" {
  description = "How often to poll SonarQube for new issues"
  type        = string
  default     = "60"
}
