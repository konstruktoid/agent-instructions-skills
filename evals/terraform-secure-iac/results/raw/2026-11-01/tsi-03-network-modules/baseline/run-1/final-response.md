I made the changes, but I couldn't validate them. `terraform init` failed because `git.example.com` (the labels module's source) isn't reachable from here, so the registry VPC module wasn't installed either. `terraform fmt -check` printed nothing, so formatting is fine.

- **`versions.tf`**: the AWS provider constraint changed from `>= 4.0` to `~> 6.0`.
- **`vpc.tf`** (new): uses `terraform-aws-modules/vpc/aws` at `~> 6.0`, with two private subnets in `eu-north-1a` and `eu-north-1b`.
  - The VPC is named `network-<environment>`.
  - It has no public subnets and no NAT gateway, so the private subnets have no outbound internet. If you need that, set `enable_nat_gateway = true` and add public subnets.
  - Tags come from `module.labels.tags`, the same source the provider's `default_tags` uses. I assumed that output exists because `providers.tf` already uses it.
- **`variables.tf`**: added `vpc_cidr` (default `10.0.0.0/16`) and `private_subnet_cidrs` (default `10.0.1.0/24` and `10.0.2.0/24`). I picked these defaults, so change them if they overlap with your existing ranges.

When you can reach the labels repo, run `terraform init -upgrade` and `terraform validate`. If the state was created under a 4.x or 5.x provider, check the `plan` output for provider-6 changes before applying.
