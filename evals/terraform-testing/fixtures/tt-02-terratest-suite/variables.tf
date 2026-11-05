variable "name" {
  description = "Name of the service."
  type        = string
}

variable "host" {
  description = "Host the service listens on."
  type        = string
}

variable "port" {
  description = "Port the service listens on."
  type        = number
  default     = 8443
}
