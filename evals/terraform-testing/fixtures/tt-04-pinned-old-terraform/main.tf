resource "terraform_data" "owned" {
  input = {
    team = var.team
    name = var.name
  }
}
