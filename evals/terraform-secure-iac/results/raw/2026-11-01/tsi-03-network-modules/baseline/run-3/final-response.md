I made the changes, but I couldn't run `terraform validate`. `terraform init` failed because `git.example.com` (the labels module source) doesn't resolve from this sandbox. I haven't checked the config against the real providers or modules.

- **Provider:** `versions.tf` now pins `hashicorp/aws` to `~> 6.0` instead of `>= 4.0`.
- **VPC:** `main.tf` has a new `module "vpc"` using `terraform-aws-modules/vpc/aws` at `~> 6.0`.
  - It's named `network-${var.environment}`.
  - It has two private subnets, one in `eu-north-1a` and one in `eu-north-1b`.
  - I created no public subnets, NAT gateways or internet gateway, since you asked for private subnets only.
- **Tagging:** the VPC module gets `tags = module.labels.tags`. The provider's `default_tags` still comes from the labels module too.
- **Variables:** `variables.tf` has two new variables, `vpc_cidr` (default `10.0.0.0/16`) and `private_subnet_cidrs` (default `10.0.1.0/24` and `10.0.2.0/24`). I picked those CIDRs, so change them if they overlap anything you use.

Run `terraform init -upgrade && terraform validate` somewhere that can reach the labels repo. That will also create the lock file for the new provider version.
