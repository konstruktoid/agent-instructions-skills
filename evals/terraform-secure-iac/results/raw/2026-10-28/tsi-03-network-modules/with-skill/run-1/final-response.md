I upgraded the AWS provider to 6.x and added the VPC with two private subnets. I couldn't run `terraform validate`, so the new config is only checked by `terraform fmt`.

`terraform init -backend=false` failed because the `labels` module source, `git.example.com`, doesn't resolve from here. Without a successful init, `validate` can't run. `tflint` isn't installed, and the repo has no scanner configured.

**What changed**
- **`versions.tf`:**
  - The AWS provider constraint went from `>= 4.0` to `~> 6.0`.
  - I added `required_version = ">= 1.10"`. The S3 backend's `use_lockfile` needs at least that, but the config had no Terraform version constraint.
- **`vpc.tf` (new):**
  - It uses `terraform-aws-modules/vpc/aws`, pinned to the exact version 6.7.3, the latest on the registry.
  - The two private subnets are in `eu-north-1a` and `eu-north-1b`, with the NAT gateway off.
  - It passes `tags = module.labels.tags`. The provider's `default_tags` already tag resources from the labels module, so this just makes it explicit.
  - The VPC is named `network-<environment>`.
- **`variables.tf`:** I added `vpc_cidr` (`10.0.0.0/16`), `availability_zones` and `private_subnet_cidrs` (`10.0.1.0/24`, `10.0.2.0/24`). These CIDR ranges are placeholders, so replace them with your real ranges.
- **`.gitignore` (new):** it excludes `.terraform/`, state files, plan files and `*.tfvars`, which the repo didn't ignore before.

**Still to do**
- Run `terraform init`, `validate` and `tflint` where the labels module is reachable.
- Commit `.terraform.lock.hcl`. Generating it needs a working init, and you should run `terraform providers lock` for every platform your CI and developers use.
- The `labels` module source has no `?ref=`, so it tracks the default branch. I left it alone because I don't know the right tag or SHA. Pin it to a commit or a protected tag.
- The private subnets have no route out to the internet. Add a NAT gateway or VPC endpoints if workloads in them need egress.

I haven't committed anything.
