# =============================================================================
# Outputs - SonarQube Code Janitor Terraform Configuration
# =============================================================================

output "resource_group_name" {
  description = "Name of the resource group"
  value       = azurerm_resource_group.main.name
}

output "container_registry_login_server" {
  description = "Login server for the container registry"
  value       = azurerm_container_registry.acr.login_server
}

output "container_registry_name" {
  description = "Name of the container registry"
  value       = azurerm_container_registry.acr.name
}

output "container_registry_username" {
  description = "Admin username for the container registry"
  value       = azurerm_container_registry.acr.admin_username
  sensitive   = true
}

output "container_registry_password" {
  description = "Admin password for the container registry"
  value       = azurerm_container_registry.acr.admin_password
  sensitive   = true
}

output "postgres_host" {
  description = "PostgreSQL server FQDN"
  value       = azurerm_postgresql_flexible_server.postgres.fqdn
}

output "application_url" {
  description = "Public URL for the frontend application"
  value       = "http://${azurerm_container_group.containers.fqdn}"
}

output "sonarqube_url" {
  description = "Public URL for SonarQube"
  value       = "http://${azurerm_container_group.containers.fqdn}:9000"
}

output "backend_url" {
  description = "Public URL for the backend API"
  value       = "http://${azurerm_container_group.containers.fqdn}:8000"
}

output "storage_account_name" {
  description = "Name of the storage account"
  value       = azurerm_storage_account.storage.name
}

output "deployment_summary" {
  description = "Deployment summary"
  value = <<-EOT
    ╔════════════════════════════════════════════════════════════════╗
    ║       SonarQube Code Janitor - Deployment Summary            ║
    ╚════════════════════════════════════════════════════════════════╝
    
    📍 Application URLs:
       Frontend:  http://${azurerm_container_group.containers.fqdn}
       SonarQube: http://${azurerm_container_group.containers.fqdn}:9000
       Backend:   http://${azurerm_container_group.containers.fqdn}:8000
    
    🔐 SonarQube Credentials:
       Username: admin
       Password: admin (CHANGE THIS IMMEDIATELY!)
    
    📦 Azure Resources:
       Resource Group: ${azurerm_resource_group.main.name}
       Registry:       ${azurerm_container_registry.acr.login_server}
       Database:       ${azurerm_postgresql_flexible_server.postgres.fqdn}
    
    💰 Estimated Monthly Cost: ~$50-60 USD
       - PostgreSQL Flexible Server (B1ms): ~$18
       - Container Instances:               ~$25-30
       - Storage Account:                   ~$3
       - Container Registry (Basic):        ~$5
    
    📝 Next Steps:
       1. Visit SonarQube and change admin password
       2. Generate a SonarQube token
       3. Update deployment: terraform apply -var="sonarqube_token=YOUR_TOKEN"
  EOT
}
