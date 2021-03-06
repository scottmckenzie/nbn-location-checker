resource "azurerm_cosmosdb_account" "db" {
  name                = local.cosmosdb_acct_name
  location            = var.location
  resource_group_name = azurerm_resource_group.rg.name
  enable_free_tier    = true
  offer_type          = "Standard"

  consistency_policy {
    consistency_level = "Session"
  }

  geo_location {
    location          = var.location
    failover_priority = 0
  }
}

resource "azurerm_cosmosdb_sql_database" "db" {
  name                = local.cosmos_db_name
  resource_group_name = azurerm_resource_group.rg.name
  account_name        = azurerm_cosmosdb_account.db.name
  throughput          = 1000
}

resource "azurerm_cosmosdb_sql_container" "locations" {
  name                = "locations"
  resource_group_name = azurerm_resource_group.rg.name
  account_name        = azurerm_cosmosdb_account.db.name
  database_name       = azurerm_cosmosdb_sql_database.db.name
  partition_key_path  = "/csa_id"
}

resource "azurerm_cosmosdb_sql_container" "subs" {
  name                = "subs"
  resource_group_name = azurerm_resource_group.rg.name
  account_name        = azurerm_cosmosdb_account.db.name
  database_name       = azurerm_cosmosdb_sql_database.db.name
  partition_key_path  = "/id"

  unique_key {
    paths = ["/email"]
  }
}

resource "azurerm_cosmosdb_sql_container" "stats" {
  name                = "stats"
  resource_group_name = azurerm_resource_group.rg.name
  account_name        = azurerm_cosmosdb_account.db.name
  database_name       = azurerm_cosmosdb_sql_database.db.name
  partition_key_path  = "/id"
}
