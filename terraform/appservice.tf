resource "azurerm_service_plan" "app" {
  name                = local.plan_name
  location            = var.location
  resource_group_name = azurerm_resource_group.rg.name
  os_type             = "Linux"
  sku_name            = "Y1"
  tags                = {}
}

resource "azurerm_storage_account" "app" {
  name                     = local.storage_account_name
  location                 = var.location
  resource_group_name      = azurerm_resource_group.rg.name
  account_replication_type = "LRS"
  account_tier             = "Standard"
  tags                     = {}
}

resource "azurerm_storage_queue" "subcheck" {
  name                 = "subscription-check-v2"
  storage_account_name = azurerm_storage_account.app.name
}

resource "azurerm_application_insights" "ai01" {
  name                = local.ai_name
  location            = var.location
  resource_group_name = azurerm_resource_group.rg.name
  application_type    = "web"
  tags                = {}
}

resource "azurerm_linux_function_app" "app" {
  name                       = local.function_app_name
  location                   = var.location
  resource_group_name        = azurerm_resource_group.rg.name
  builtin_logging_enabled    = false
  https_only                 = true
  service_plan_id            = azurerm_service_plan.app.id
  storage_account_name       = azurerm_storage_account.app.name
  storage_account_access_key = azurerm_storage_account.app.primary_access_key

  app_settings = {
    "AzureCosmosDBConnectionString"                 = "${azurerm_cosmosdb_account.db.connection_strings[0]}"
    "AzureWebJobs.ProcessSubscriptions_v2.Disabled" = true
    "AzureWebJobsSendGridApiKey"                    = "${var.sendgrid_api_key}"
    "CheckLocations_v2.Schedule"                    = "0 5 11 * * *"
    "FUNCTIONS_WORKER_RUNTIME"                      = "python"
    "ProcessSubscriptions_v2.Schedule"              = "0 5 11 * * *"
    "WEBSITE_RUN_FROM_PACKAGE"                      = "https://${azurerm_storage_account.app.name}.blob.core.windows.net/${azurerm_storage_container.app.name}/${azurerm_storage_blob.app.name}${data.azurerm_storage_account_blob_container_sas.app.sas}"
  }

  site_config {
    application_stack {
      python_version = "3.9"
    }
    application_insights_connection_string = azurerm_application_insights.ai01.connection_string
    ftps_state                             = "Disabled"
    http2_enabled                          = true
  }

  lifecycle {
    ignore_changes = [
      tags["hidden-link: /app-insights-conn-string"],
      tags["hidden-link: /app-insights-instrumentation-key"],
      tags["hidden-link: /app-insights-resource-id"],
      app_settings["AzureWebJobs.CheckLocations.Disabled"],
      app_settings["AzureWebJobs.CheckLocations_v2.Disabled"],
      app_settings["AzureWebJobs.LocationChecker_v2.Disabled"],
      app_settings["AzureWebJobs.MigrateOneLocation.Disabled"],
      app_settings["AzureWebJobs.MigrateOneSubscription.Disabled"],
      app_settings["AzureWebJobs.ProcessSubscriptions_v2.Disabled"],
      app_settings["CheckLocations_v2.Schedule"],
      app_settings["ProcessSubscriptions_v2.QueueName"],
      app_settings["ProcessSubscriptions_v2.Schedule"],
    ]
  }
}
