The AWS provider is now on the 6.x line and the config has a VPC with two private subnets. I could only validate it with the labels module stubbed out, so it hasn't been checked end to end.

**What changed**
- **Provider:** `versions.tf` now pins `hashicorp/aws` to `~> 6.0`, and the lock file resolves it to 6.72.0. I also added `required_version = ">= 1.10"`, which `use_lockfile` on the S3 backend needs.
- **VPC:** `main.tf` has a `vpc` module from `terraform-aws-modules/vpc/aws`, pinned to exactly `6.7.3`. It sets `tags = module.labels.tags`, and the provider's `default_tags` still applies as before.
- **Variables:** `variables.tf` has three new inputs: `vpc_cidr` (`10.0.0.0/16`), `availability_zones` (`eu-north-1a`, `eu-north-1b`) and `private_subnet_cidrs` (`10.0.1.0/24`, `10.0.2.0/24`). The CIDRs are placeholders, so change them to fit your address plan.
- **Lock file:** `.terraform.lock.hcl` is new and records checksums for linux and darwin on amd64 and arm64. A disk-quota message appeared while it was generated. The file has the expected hashes, but regenerate it if `init` complains.

**Checks**
- **Passed:** `terraform fmt` is clean. `terraform validate` passes with a local stub standing in for the labels module, which also confirmed the 6.x provider works with the VPC module.
- **Not run:** The real `terraform init` fails because `git.example.com` doesn't resolve from here, so the labels module never downloaded. That also means `terraform validate` didn't run against the real config. `tflint` isn't installed here. I did no backend-enabled `init` or `plan`, since there are no credentials.
- **checkov:** It flags `CKV_TF_1` (module sources should use a commit hash) on the VPC module. I left it because a registry module with an exact version is the pin the repo guidance asks for. Checkov did not scan the labels module.

**For you to follow up**
- The labels module `source` has no `?ref=` pin, so it follows the default branch. I couldn't look up a SHA or protected tag from here, so I left it. Pin it before merging.
- Run `terraform init`, `validate`, and a `plan` saved to a path outside the repo with non-production credentials, and read the plan before applying. Bumping the provider from `>= 4.0` to 6.x can change defaults on other resources, though this config declares none.
- The VPC module's defaults create no NAT gateway or internet gateway, so these subnets have no outbound route.
