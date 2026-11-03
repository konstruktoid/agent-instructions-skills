I made the changes, but I couldn't validate them. `terraform init` fails because `git.example.com` (the labels module source) doesn't resolve from this environment. `terraform fmt -check` passes, but `terraform validate` couldn't run.

- **Provider:** `versions.tf` now pins `hashicorp/aws` to `~> 6.0`, where it was `>= 4.0`.
- **VPC:** `main.tf` has a new `module "vpc"` from `terraform-aws-modules/vpc/aws`, version `~> 6.0`.
  - Its name is `network-${var.environment}`.
  - It has two private subnets, `10.0.1.0/24` and `10.0.2.0/24`, in `eu-north-1a` and `eu-north-1b`.
  - NAT is disabled, since you only asked for private subnets. Add `enable_nat_gateway = true` if they need outbound internet access.
- **Variables:** `variables.tf` gains `vpc_cidr`, `availability_zones` and `private_subnet_cidrs`, with those values as defaults.
- **Tagging:** the provider's `default_tags` still use `module.labels.tags`, and the VPC module also gets `tags = module.labels.tags`.

Run `terraform init -upgrade` and `terraform plan` somewhere that can reach the labels repo. That will also create the lock file at the 6.x provider version.
