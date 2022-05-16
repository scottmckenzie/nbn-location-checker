data "archive_file" "app" {
  type        = "zip"
  source_dir  = "../src"
  output_path = "function-app.zip"
}

resource "azurerm_storage_container" "app" {
  name                  = "content"
  storage_account_name  = azurerm_storage_account.app.name
  container_access_type = "private"
}

resource "azurerm_storage_blob" "app" {
  name                   = "function-app.zip"
  storage_account_name   = azurerm_storage_account.app.name
  storage_container_name = azurerm_storage_container.app.name
  content_md5            = data.archive_file.app.output_md5
  type                   = "Block"
  source                 = data.archive_file.app.output_path
}

data "azurerm_storage_account_blob_container_sas" "app" {
  connection_string = azurerm_storage_account.app.primary_connection_string
  container_name    = azurerm_storage_container.app.name

  start  = "2022-01-01T00:00:00Z"
  expiry = "2032-01-01T00:00:00Z"

  permissions {
    read   = true
    add    = false
    create = false
    write  = false
    delete = false
    list   = false
  }
}
