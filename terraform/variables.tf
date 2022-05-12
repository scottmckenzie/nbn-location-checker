#########################################################################################
# REQUIRED VARIABLES
#########################################################################################

variable "sendgrid_api_key" {
  type        = string
  description = "SendGrid API key"
  sensitive   = true
}


#########################################################################################
# OPTIONAL VARIABLES (sane defaults)
#########################################################################################

variable "app_name" {
  type        = string
  description = "The application name"
  default     = "nbn-address-checker"
}

variable "environment" {
  type        = string
  description = "Environment tag"
  default     = "prd"
}

variable "location" {
  type        = string
  description = "Azure region resources will be created"
  default     = "australiaeast"
}
