resource "azurerm_service_plan" "app" {
  name                = local.plan_name
  location            = var.location
  resource_group_name = azurerm_resource_group.rg.name
  os_type             = "Linux"
  sku_name            = "Y1"
}

resource "azurerm_storage_account" "app" {
  name                     = local.storage_account_name
  location                 = var.location
  resource_group_name      = azurerm_resource_group.rg.name
  account_replication_type = "LRS"
  account_tier             = "Standard"
}

resource "azurerm_application_insights" "app" {
  name                = local.app_insights_name
  location            = var.location
  resource_group_name = azurerm_resource_group.rg.name
  application_type    = "web"
}

resource "azurerm_linux_function_app" "app" {
  name                       = local.function_app_name
  location                   = var.location
  resource_group_name        = azurerm_resource_group.rg.name
  https_only                 = true
  service_plan_id            = azurerm_service_plan.app.id
  storage_account_name       = azurerm_storage_account.app.name
  storage_account_access_key = azurerm_storage_account.app.primary_access_key

  app_settings = {
    "FUNCTIONS_WORKER_RUNTIME" = "python"
    "SCM_DO_BUILD_DURING_DEPLOYMENT" = "true"
    "WEBSITE_RUN_FROM_PACKAGE" = "https://${azurerm_storage_account.app.name}.blob.core.windows.net/${azurerm_storage_container.app.name}/${azurerm_storage_blob.app.name}${data.azurerm_storage_account_blob_container_sas.app.sas}"
  }

  site_config {
    application_stack {
      python_version = "3.9"
    }
    application_insights_connection_string = azurerm_application_insights.app.connection_string
    application_insights_key               = azurerm_application_insights.app.instrumentation_key
    ftps_state                             = "Disabled"
    http2_enabled                          = true
  }
}
