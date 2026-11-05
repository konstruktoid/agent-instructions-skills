output "service_name" {
  description = "Name of the service."
  value       = "svc-${var.name}"
}

output "endpoint" {
  description = "Address clients use to reach the service."
  value       = "https://${var.host}/${var.port}"
}
