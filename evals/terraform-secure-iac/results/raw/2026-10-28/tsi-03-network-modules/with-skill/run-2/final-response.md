I moved the config to the 6.x AWS provider and added the VPC with two private subnets. Only `terraform fmt` passes. `terraform init` and `terraform validate` failed because the labels module couldn't be downloaded, and I didn't run `tflint` or a plan.

**Changes**
- `versions.tf`: the AWS provider constraint goes from `>= 4.0` to `~> 6.0`. I also added `required_version = ">= 1.10"`. The existing S3 backend uses `use_lockfile`, which needs 1.10 or later.
- `main.tf`: the new `module "vpc"` uses `terraform-aws-modules/vpc/aws` pinned to exactly `6.7.3`, the latest registry version when I checked.
  - Its availability zones are `"${var.region}a"` and `"${var.region}b"`, which are eu-north-1a and eu-north-1b at the default region.
  - It creates private subnets only, with no NAT gateway or internet gateway.
  - It takes `tags = module.labels.tags`. The provider's `default_tags` already apply the same tags, so this just makes the tagging explicit.
- `variables.tf`: new `vpc_cidr` (default `10.0.0.0/16`) and `private_subnet_cidrs` (default `10.0.1.0/24` and `10.0.2.0/24`). The subnet list has a validation that it holds exactly two entries.

**Verification**
- `terraform fmt -recursive -check -diff` is clean.
- `terraform init -backend=false` failed. The labels module source is `git.example.com`, which doesn't resolve from here. So `validate` and `tflint` didn't run, and I haven't confirmed the config against provider 6.x or the 6.7.3 module schema.
- No plan was run, because I had no credentials or backend access.
- Please run `init` and `validate` where that host is reachable.

**Things to check**
- **Unpinned labels module:** its source has no `?ref=`, so it follows whatever the default branch is. I left it alone because you didn't ask me to change it. I'd pin it to a commit SHA or a protected release tag.
- **VPC name:** I named the VPC `network-${var.environment}` because I couldn't see which outputs the labels module exposes. Its tags are still applied.
- **No lock file:** `.terraform.lock.hcl` isn't in the repo, and `init` couldn't generate it. Once `init` works, commit it and run `terraform providers lock` for every platform CI uses.
- **Upgrade risk:** going from 4.x to 6.x can change resource defaults. Plan against a non-production root before applying.

I haven't committed anything.
