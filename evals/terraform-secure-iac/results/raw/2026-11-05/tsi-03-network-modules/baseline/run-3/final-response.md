I've made the changes, but I couldn't validate them. `terraform init` fails because `git.example.com` (the labels module's source) doesn't resolve from this sandbox, so `terraform validate` couldn't run either. `terraform fmt -check` passes. I removed the partial `.terraform` directory and lockfile that the failed init left behind.

- **`versions.tf`**: the AWS provider constraint changed from `>= 4.0` to `~> 6.0`.
- **`main.tf`**: I added a `vpc` module from `terraform-aws-modules/vpc/aws`, pinned to `~> 6.0`.
  - It has two private subnets, one in each of `eu-north-1a` and `eu-north-1b`.
  - It is named `network-${var.environment}`.
  - It is tagged with `module.labels.tags`. The provider's `default_tags` already use the same tags.
  - NAT is off (`enable_nat_gateway = false`), so the private subnets have no outbound internet. Tell me if you want NAT or other gateways.
- **`variables.tf`**: I added `vpc_cidr` (default `10.0.0.0/16`), `azs` (the two zones above) and `private_subnet_cidrs` (default `10.0.1.0/24` and `10.0.2.0/24`). I picked those CIDR ranges myself, so check they don't overlap with anything else you run.

Run `terraform init -upgrade` and `terraform validate` somewhere that can reach `git.example.com`. The upgrade also moves the provider lock to 6.x.
