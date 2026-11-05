resource "terraform_data" "service" {
  input = {
    name = var.name
    host = var.host
    port = var.port
  }
}
