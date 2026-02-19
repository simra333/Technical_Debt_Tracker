resource "azurerm_kubernetes_cluster" "aks" {
  name                = "TDT-aks-cluster"
  location            = "UKSouth"
  resource_group_name = azurerm_resource_group.rg.name
  dns_prefix          = "TDTaks"

  default_node_pool {
    name       = "default"
    node_count = 2
    vm_size    = "Standard_B2ms"
  }

  identity {
    type = "SystemAssigned"
  }

  tags = {
    Environment = "Development"
  }
}
