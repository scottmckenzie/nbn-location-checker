# Set the terraform required version
terraform {
  # Azure Pipelines terraform extension does not work with >=0.15.0
  required_version = ">=1.1"
  backend "azurerm" {
    resource_group_name  = "rg-terraform"
    storage_account_name = "stnbnterraform"
    container_name       = "terraform"
    key                  = "terraform.tfstate"
  }
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = ">=3.5"
    }
  }
}

# Configure the Microsoft Azure Provider
provider "azurerm" {
  features {}
}

# Make client_id, tenant_id, subscription_id and object_id variables
data "azurerm_client_config" "current" {}
