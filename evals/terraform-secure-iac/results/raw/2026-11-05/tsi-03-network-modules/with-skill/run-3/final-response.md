I made the changes, but I couldn't run `terraform validate` or `tflint`, so the config is only checked by `terraform fmt`, which passes.

**What changed**
- **`versions.tf`:**
  - The AWS provider constraint goes from `>= 4.0` to `~> 6.0`.
  - I also added `required_version = ">= 1.10"`, which the S3 backend's `use_lockfile` already needs.
- **`main.tf`:** a new `module "vpc"` using `terraform-aws-modules/vpc/aws`, pinned to exactly `6.7.3`, the latest version I found on the registry. It creates two private subnets, one in each availability zone, and no public subnets or NAT gateways.
- **`variables.tf`:**
  - `vpc_cidr` defaults to `10.0.0.0/16`.
  - `availability_zones` defaults to `["eu-north-1a", "eu-north-1b"]`.
  - `private_subnet_cidrs` defaults to `10.0.1.0/24` and `10.0.2.0/24`.
- **Tagging:** all tags still come from `module.labels.tags` through the provider's `default_tags`, which the VPC and subnets inherit. I didn't add a separate `tags` argument on the VPC module. I also named the VPC `network-${var.environment}` rather than guessing at a key in the labels output.
- **`.gitignore`:** new, covering `.terraform/`, state files, plan files and crash logs.

**Not verified**
- **`terraform init` fails.** The labels module's source, `git.example.com/platform/terraform-labels.git`, doesn't resolve from here, so `init` stops before it gets to validate.
- **No `tflint` or scanner.** `tflint` isn't installed and the repo configures no scanner.
- **No lock file.** `.terraform.lock.hcl` doesn't exist, and I couldn't create one without a successful `init`. Once you can reach the labels module, run `terraform init`, then `terraform providers lock` for the platforms CI uses, and commit the result.
- **No plan.** I had no credentials to run one, so I haven't checked what the VPC module will create.

**Pre-existing issues I left alone**
- The labels module source has no `?ref=` pin, so it floats with the repo's default branch. Pin it to a commit SHA or a protected tag.
- The 6.x provider is a major bump, so read the plan for any forced replacements before applying it.
