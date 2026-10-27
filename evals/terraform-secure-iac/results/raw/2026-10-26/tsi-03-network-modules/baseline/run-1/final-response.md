I made the changes, but I couldn't validate them. `terraform init` fails because `git.example.com` (the labels module's source) doesn't resolve from this environment. `terraform fmt -check` passed.

- **Provider (`versions.tf`):** the AWS provider constraint went from `>= 4.0` to `~> 6.0`.
- **Variables (`variables.tf`):** I added `vpc_cidr` (`10.0.0.0/16`), `availability_zones` (`eu-north-1a` and `eu-north-1b`) and `private_subnet_cidrs` (`10.0.1.0/24` and `10.0.2.0/24`).
- **VPC (`main.tf`):** a new `module "vpc"` uses `terraform-aws-modules/vpc/aws` at `~> 6.0`, named `network-${var.environment}`. It creates only the two private subnets, with no public subnets and no NAT gateway. I set `enable_nat_gateway = false`, so the subnets have no outbound internet access. If workloads in them need that, you'll want public subnets and a NAT gateway.
- **Tagging:** the module gets `tags = module.labels.tags`. The provider's `default_tags` already uses the same tags, so they're applied twice with the same values. Passing them explicitly just keeps the module's tagging independent of the provider defaults.

Run `terraform init -upgrade` and `terraform plan` somewhere that can reach the labels repo. If the lock file was ever committed, the upgrade is also what moves it to 6.x.
