I made the changes, but I couldn't validate them. `terraform init` fails because `git.example.com` (the labels module source) can't be resolved from this environment. `terraform fmt -check` reported nothing. I removed the `.terraform` directory that `init` left behind.

- **Provider (`versions.tf`):** the AWS provider constraint changes from `>= 4.0` to `~> 6.0`.
- **VPC (`main.tf`):** I added a `terraform-aws-modules/vpc/aws` module at `~> 6.0`.
  - It is named `network-${var.environment}`.
  - It has two private subnets in `eu-north-1a` and `eu-north-1b`. The zones come from `var.region`.
  - It sets `tags = module.labels.tags`. The provider's `default_tags` from the labels module still applies too.
- **Variables (`variables.tf`):**
  - `vpc_cidr` defaults to `10.0.0.0/16`.
  - `private_subnet_cidrs` defaults to `10.0.1.0/24` and `10.0.2.0/24`. Change these if they clash with existing ranges.
- **No NAT gateway:** I set `enable_nat_gateway = false`, so the private subnets have no outbound internet. Turn it on if workloads need it, since it adds cost.
- **Unpinned labels module:** its git source has no `?ref=`, so it tracks the default branch. I left it as is, but pinning a tag would be safer.
- **Lock file:** there is no `.terraform.lock.hcl` in the repo. Run `terraform init -upgrade` where the labels module is reachable, and commit the lock file.

I haven't committed anything.
