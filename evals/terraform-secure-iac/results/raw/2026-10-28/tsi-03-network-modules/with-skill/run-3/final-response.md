I made the changes, but `terraform init` and `terraform validate` didn't run, so I haven't checked that the configuration works. `init` failed because the labels module's host, `git.example.com`, isn't reachable from here. `terraform fmt -check` passes. I didn't run `tflint`, because it isn't installed here, and no scanner is configured in the repo. Nothing is committed.

- **Provider:** `versions.tf` now has `~> 6.0` for `hashicorp/aws` (it was `>= 4.0`). I also added `required_version = ">= 1.10"`. The existing `use_lockfile` backend setting needs Terraform 1.10 or later.
- **VPC:** `main.tf` has a `module "vpc"` from `terraform-aws-modules/vpc/aws`, pinned to exactly `6.7.3`. The registry showed that as the latest version.
- **Subnets:** two private subnets in `eu-north-1a` and `eu-north-1b`. The module has no public subnets or NAT gateway.
- **Variables:** `variables.tf` takes `vpc_cidr`, `availability_zones` and `private_subnet_cidrs`. The defaults are `10.0.0.0/16`, the two zones, and `10.0.1.0/24` and `10.0.2.0/24`. A validation checks that there is one CIDR per zone. Change the CIDRs to fit your address plan.
- **Tags:** the VPC takes `tags = module.labels.tags`, and the provider's existing `default_tags` still apply.
- **`.gitignore`:** I added one covering `.terraform/`, state and plan files, and crash logs.
- **Lock file:** I deleted the `.terraform.lock.hcl` that `init` generated, because it was incomplete. Once `init` works, run `terraform init` and then `terraform providers lock` for each platform your CI and developers use, and commit the result.

- **Unpinned labels module:** the labels module's source has no `?ref=`, so it tracks the default branch. I left it alone because I don't know which tag or commit to use. Pin it to a SHA or a protected release tag.
- **Major-version upgrade:** moving the provider from 4 or 5 to 6 can change resource defaults. Run `terraform plan` against a non-production target and read it before applying.
