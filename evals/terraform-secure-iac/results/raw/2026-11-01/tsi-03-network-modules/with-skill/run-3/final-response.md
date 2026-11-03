I moved the config to the 6.x AWS provider and added the VPC with two private subnets. `terraform fmt` is clean and `terraform validate` passes, but only in a temporary copy that swaps the labels module for a stub. I couldn't run a normal `init` here.

**Changes**
- **Provider:** `versions.tf` now pins `hashicorp/aws` to `~> 6.28`. I chose 6.28 because the VPC module's own constraint is `>= 6.28`. I also added `required_version = ">= 1.10"`, since the config had none.
- **VPC:** `main.tf` adds `terraform-aws-modules/vpc/aws` at exactly `6.7.3`, which is the latest version I found on the registry.
  - The VPC has two private subnets in eu-north-1a and eu-north-1b.
  - I turned off the internet gateway and NAT gateway because you asked for private subnets only. Say so if you want NAT.
  - The VPC name is `network-<environment>`.
- **Variables:** `variables.tf` adds `vpc_cidr`, `availability_zones` and `private_subnet_cidrs`, so the CIDRs aren't hardcoded in the resource. The defaults are `10.0.0.0/16`, `10.0.1.0/24` and `10.0.2.0/24`. A validation checks that there is one CIDR per zone.
- **Outputs:** a new `outputs.tf` exposes `vpc_id` and `private_subnet_ids`.
- **Tagging:** the provider's `default_tags` already comes from the labels module, and I also pass `tags = module.labels.tags` to the VPC module.

**Checks**
- **Real `init`:** it failed because `git.example.com` doesn't resolve from this sandbox. So the real labels module was never loaded, and I haven't confirmed that it exposes `tags`, which the existing code already relies on.
- **Lock file:** there is no `.terraform.lock.hcl` in the repo, and I didn't create one. You'll need to run `terraform init` and `terraform providers lock` for your CI platforms, then commit the result.
- **tflint and plan:** `tflint` isn't installed here, and I didn't run a plan because there are no credentials.
- **checkov:** it reported one finding, `CKV_TF_1`, which wants module sources pinned to a commit hash. The registry module is pinned to an exact version, which is the right form for a registry source, so I'm leaving that finding as it is.

**Existing problem I didn't change**
The labels module `source` has no `?ref=`, so it follows the default branch. That is a supply-chain risk, and it's why this change isn't reproducible. I don't know a good SHA or tag, so I left it. Please pin it to a commit SHA or a protected tag.

**Upgrade risk**
Going from `>= 4.0` to 6.x is a big jump. The existing config declares no AWS resources, so there is little to break. Still, run a plan against a non-production environment before you apply.

I haven't committed anything.
