I've made the changes, but I couldn't validate them. `terraform init` fails because `git.example.com`, where the labels module lives, isn't reachable from here. `terraform fmt -check` reported no formatting problems.

- **Provider:** `versions.tf` now pins `hashicorp/aws` to `~> 6.0` instead of `>= 4.0`.
- **VPC:** `main.tf` has a new `module "vpc"` using `terraform-aws-modules/vpc/aws` at `~> 6.0`.
  - It creates two private subnets in `eu-north-1a` and `eu-north-1b`, built as `["${var.region}a", "${var.region}b"]`.
  - It has no public subnets and no NAT gateway.
- **Tagging:** the VPC module gets `tags = module.labels.tags`. The provider's `default_tags` already used the labels module, so that is unchanged.
- **Variables:** `variables.tf` has two new variables I picked: `vpc_cidr` (default `10.0.0.0/16`) and `private_subnet_cidrs` (default `10.0.1.0/24` and `10.0.2.0/24`). Change them if those ranges clash with anything.
- **Outputs:** a new `outputs.tf` exposes `vpc_id` and `private_subnet_ids`.

The VPC name is set to `network-${var.environment}`.

Run `terraform init -upgrade` and `terraform validate` somewhere that can reach the labels module. The upgrade is needed because the provider version changed. Provider 6.x has some breaking changes from 4.x, but this config only uses the provider block and `default_tags`, which I wouldn't expect to be affected.
