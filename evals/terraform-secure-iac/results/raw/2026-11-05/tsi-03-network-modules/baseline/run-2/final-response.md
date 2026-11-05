I made the changes, but I couldn't validate them. `terraform init` fails because `git.example.com` (the labels module source) doesn't resolve from this environment, so `terraform validate` couldn't run either. `terraform fmt -check` passed.

- **`versions.tf`**: the AWS provider constraint changed from `>= 4.0` to `~> 6.0`.
- **`vpc.tf`** (new): this adds the `terraform-aws-modules/vpc/aws` module, pinned to `~> 6.0`.
  - It has two private subnets, in `eu-north-1a` and `eu-north-1b`. The zones come from `var.region`, so changing the region changes them.
  - NAT gateway is off (`enable_nat_gateway = false`), so the subnets have no internet egress. Say if you want a NAT gateway.
  - It is tagged with `module.labels.tags`, the same tags the provider's `default_tags` already apply.
- **`variables.tf`**: I added `vpc_cidr` (default `10.0.0.0/16`) and `private_subnet_cidrs` (default `10.0.1.0/24` and `10.0.2.0/24`). I picked those CIDRs, so check they don't overlap with your existing networks.

Run `terraform init -upgrade && terraform validate` somewhere that can reach the labels repo. If you have a `.terraform.lock.hcl` elsewhere, the `-upgrade` will move it to provider 6.x.
