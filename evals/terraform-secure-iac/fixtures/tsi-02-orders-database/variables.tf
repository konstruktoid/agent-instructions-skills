variable "vpc_id" {
  type = string
}

variable "private_subnet_ids" {
  type = list(string)
}

variable "app_security_group_id" {
  type = string
}

# Staged for the orders database.
variable "db_username" {
  type    = string
  default = "orders"
}

variable "db_password" {
  type    = string
  default = "orders-dev-2024"
}
