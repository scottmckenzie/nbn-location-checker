locals {
  app_insights_name    = format("appi-%s", var.app_name)
  function_app_name    = format("func-%s", var.app_name)
  plan_name            = format("plan-%s", var.app_name)
  resource_group_name  = format("rg-%s", var.app_name)
  storage_account_name = format("stfunc%s", substr(replace(var.app_name, "-", ""), 0, 18))
}

resource "azurerm_resource_group" "rg" {
  name     = local.resource_group_name
  location = var.location
  tags     = {}
}
