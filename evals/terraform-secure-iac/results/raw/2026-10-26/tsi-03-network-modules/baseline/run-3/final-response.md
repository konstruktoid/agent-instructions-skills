I made the changes, but I couldn't run `terraform init` or `validate`. The `labels` module is pulled from `git.example.com`, which doesn't resolve from this environment. `terraform fmt -check` passes. I removed the partial `.terraform/` directory that the failed init left behind.

- **Provider:** `versions.tf` now pins `hashicorp/aws` to `~> 6.0` (it was `>= 4.0`).
- **VPC:** the new `vpc.tf` uses `terraform-aws-modules/vpc/aws` at `~> 6.0`.
  - It has two private subnets, in `eu-north-1a` and `eu-north-1b`. The zones come from `var.region`.
  - NAT gateway is off (`enable_nat_gateway = false`) and there are no public subnets, so the subnets have no internet egress. Say so if you want NAT added.
- **Tagging:** the module gets `tags = module.labels.tags`, and the provider's `default_tags` still uses the same tags.
- **New variables:** `vpc_cidr` defaults to `10.0.0.0/16`. `private_subnet_cidrs` defaults to `["10.0.1.0/24", "10.0.2.0/24"]`. I picked these ranges, so check they don't overlap anything you peer with.
- **Name:** the VPC name is `"${var.environment}-network"`. I didn't use the labels module for it because I don't know what outputs it exposes.

Run `terraform init -upgrade` where the labels repo is reachable. It will update the lock file, and the provider move from 4.x to 6.x may need a look at the plan output.
