I've moved the config to the 6.x AWS provider and added the VPC. `terraform validate` only passed on a temporary copy with a stub labels module, because the real one can't be downloaded here. It isn't committed, and I haven't written a lock file or run tflint.

**Changes**
- **`versions.tf`:** the AWS provider is now `~> 6.28` (it was `>= 4.0`), and I added `required_version = ">= 1.10"`. The VPC module needs provider 6.28 or later, and the existing `use_lockfile` backend setting needs Terraform 1.10 or later.
- **`vpc.tf` (new):** `terraform-aws-modules/vpc/aws`, pinned to exactly `6.7.3`. It creates two private subnets in `eu-north-1a` and `eu-north-1b`, built from `var.region`. NAT gateways are off, so the subnets have no internet egress. Say if you want one.
- **`variables.tf`:** new `vpc_cidr` (default `10.0.0.0/16`) and `private_subnet_cidrs` (defaults `10.0.1.0/24` and `10.0.2.0/24`). These CIDRs are placeholders, so change them to fit your address plan.
- **Tagging:** every resource, including the VPC module's, is tagged from `module.labels.tags` through the provider's `default_tags`.

**Checks**
- `terraform fmt` is clean.
- `terraform init -backend=false` fails in the real directory: `git.example.com`, the labels module's source, doesn't resolve from this sandbox.
- On the temporary copy, validate succeeded and resolved the provider to 6.71.0. I deleted the copy, and `.terraform` and the lock file are not in the repo.
- tflint isn't installed here.

**Left unchanged: the labels module is unpinned.** `main.tf` sources it from a Git URL with no `?ref=`, so it follows the default branch. I don't know a valid commit SHA or protected tag, so I didn't guess one. Please pin it to a SHA or protected tag.

**Before merging:** run `terraform init` where `git.example.com` is reachable, then commit `.terraform.lock.hcl`. Generate it for every platform your CI uses with `terraform providers lock -platform=...`. Read the `terraform plan` output as well. A move from a `>= 4.0` provider to 6.x can change resource defaults.
