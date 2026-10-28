I've made the provider bump and added the VPC, but I couldn't validate any of it. `terraform init` failed because `git.example.com`, where the labels module lives, doesn't resolve from this sandbox. `terraform fmt -check` passed.

- **Provider:** in `versions.tf`, the AWS provider constraint changed from `>= 4.0` to `~> 6.0`.
- **VPC:** `main.tf` has a new `module "vpc"` using `terraform-aws-modules/vpc/aws` at `~> 6.0`. It creates two private subnets in `eu-north-1a` and `eu-north-1b`.
- **Tags:** the VPC module gets `tags = module.labels.tags`, and the provider's `default_tags` still apply.
- **Variables:** `variables.tf` has three new variables with defaults: `vpc_cidr` (`10.0.0.0/16`), `availability_zones` and `private_subnet_cidrs` (`10.0.1.0/24`, `10.0.2.0/24`). I picked these CIDRs, so change them if they clash with your address plan.
- **Naming:** the VPC is named `network-${var.environment}`. I didn't use a `Name` tag from the labels module because I can't see what tags it outputs.
- **NAT:** NAT gateways are off (`enable_nat_gateway = false`), so the private subnets have no outbound internet. Turn it on if workloads need it, though NAT adds cost.
- **Labels source:** the labels module's git source has no `?ref=` pin. I left it alone, but pinning it to a tag would make runs reproducible.

Run `terraform init -upgrade` and `terraform validate` where the labels repo is reachable. That will also create the lock file for the 6.x provider.
