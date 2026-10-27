module "labels" {
  source = "git::https://git.example.com/platform/terraform-labels.git"

  service     = "network"
  environment = var.environment
}
