resource "terraform_data" "policy" {
  input = {
    name           = var.name
    retention_days = var.retention_days
  }
}
