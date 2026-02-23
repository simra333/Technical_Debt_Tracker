resource "azurerm_container_registry" "acr" {
    name               = "tdtrackeracr"
    resource_group_name = azurerm_resource_group.rg.name
    location           = azurerm_resource_group.rg.location
    sku                = "Basic"
}

# Attach ACR to AKS
resource "azurerm_role_assignment" "aks_acr_pull" {
    scope                = azurerm_container_registry.acr.id
    role_definition_name = "AcrPull"
    principal_id         = azurerm_kubernetes_cluster.aks.identity[0].principal_id
    skip_service_principal_aad_check = true
}