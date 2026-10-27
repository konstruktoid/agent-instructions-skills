I've pinned the AWS provider to `~> 6.0` and added the VPC module, but I couldn't validate it. `terraform init` fails because `git.example.com` (the labels module source) doesn't resolve from this environment. So neither the 6.x provider nor the VPC module has been installed or checked.

- **Provider:** `versions.tf` now has `version = "~> 6.0"` instead of `>= 4.0`. There's no lockfile in the repo to update.
- **VPC:** `main.tf` has a `module "vpc"` block using `terraform-aws-modules/vpc/aws` at `~> 6.0`. It's named `network-${var.environment}` and uses `azs = ["${var.region}a", "${var.region}b"]`, which gives eu-north-1a and eu-north-1b with the default region. It has two private subnets and no public subnets.
- **Tagging:** the VPC module gets `tags = module.labels.tags`. The provider's `default_tags` still applies as before.
- **Variables:** `variables.tf` adds `vpc_cidr` (default `10.0.0.0/16`) and `private_subnet_cidrs` (default `10.0.1.0/24` and `10.0.2.0/24`). I picked those CIDRs, so change them if they clash with existing ranges.
- **NAT:** `enable_nat_gateway` is `false`, so the private subnets have no outbound internet. Turn it on if you need that.

Run `terraform init && terraform validate` somewhere that can reach the labels repo. A major provider jump from 4.x to 6.x can also affect other resources, so check `terraform plan` too.
