variable "name" {
  description = "Name of the service the policy belongs to."
  type        = string
}

variable "retention_days" {
  description = "How many days records are kept."
  type        = number
  default     = 30
}
