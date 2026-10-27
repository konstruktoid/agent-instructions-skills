I've made the changes, but `terraform validate` didn't pass. `terraform init` couldn't download the labels module because `git.example.com` doesn't resolve from here, and the VPC module was never installed either. Only `terraform fmt -check` passes. I didn't run `tflint` (it isn't installed here) or a configuration scanner.

**Changes**
- **Provider:** `versions.tf` now sets `aws` to `~> 6.0` instead of `>= 4.0`.
- **Terraform version:** I added `required_version = ">= 1.10"`. The S3 backend's `use_lockfile` needs 1.10 or later, so this makes that requirement explicit.
- **VPC:** `main.tf` has a new `module "vpc"` using `terraform-aws-modules/vpc/aws`, pinned to exactly `6.7.3` (the current registry release). It sets `azs = ["eu-north-1a", "eu-north-1b"]` and `private_subnets` from a variable, with no NAT or internet gateway.
- **Tagging:** the module gets `tags = module.labels.tags`, and the provider's `default_tags` still apply.
- **Variables:** `variables.tf` has two new variables, `vpc_cidr` (default `10.0.0.0/16`) and `private_subnet_cidrs` (default `10.0.1.0/24` and `10.0.2.0/24`). The CIDRs are placeholders I picked, so check them against your address plan.

**Still to do**
- **Labels module:** it's sourced from a Git URL with no `?ref=`, so it follows the default branch. I left it alone because I don't know the right commit SHA or tag. Pin it to one.
- **Lock file:** there is no `.terraform.lock.hcl`. Once `init` works, generate one with `terraform providers lock -platform=linux_amd64 -platform=darwin_arm64`, adjusting the platforms to what you use, and commit it.
- **Validation:** run `terraform init -backend=false`, `terraform validate` and `tflint` somewhere that can reach the labels repo.

I removed the partial `.terraform/` directory that the failed `init` left behind.
