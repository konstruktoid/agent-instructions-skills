I moved the AWS provider to 6.x and added the VPC with two private subnets, but `terraform validate` and `tflint` did not run, so the change is only partly verified. Nothing is committed.

**Changes**
- **`versions.tf`**: the AWS provider constraint went from `>= 4.0` to `~> 6.0`. I also added `required_version = ">= 1.10"`, which was missing. The `use_lockfile` setting in your S3 backend needs Terraform 1.10 or later.
- **`main.tf`**: new `module "vpc"` using `terraform-aws-modules/vpc/aws`, pinned to the exact version `6.7.3`.
  - It creates only private subnets, in `eu-north-1a` and `eu-north-1b`. There are no public subnets, internet gateway or NAT.
  - It is named `network-<environment>` and gets `tags = module.labels.tags`, on top of the provider's `default_tags`.
- **`variables.tf`**: new variables for `vpc_cidr` (`10.0.0.0/16`), `private_subnet_cidrs` (`10.0.1.0/24` and `10.0.2.0/24`) and `availability_zones`. The CIDRs are placeholders, so set them to your real address plan.
- **`.terraform.lock.hcl`**: new. It pins the AWS provider at 6.70.0 and carries checksums for linux and darwin on amd64 and arm64. Review it like any other dependency bump.

**Verification**
- `terraform fmt -check` passes.
- `terraform init -backend=false` failed on the `labels` module, because `git.example.com` can't be resolved from this sandbox.
- I validated a scratch copy with a stubbed `labels` module and no backend block. `init` downloaded the provider and the VPC module, but `validate` failed because the AWS provider binary would not start (plugin handshake error).
- `tflint` isn't installed here, and no scanner is configured in the repo.
- No plan was run because there are no credentials.

**Needs your attention**
- **Unpinned `labels` module:** its source, `git::https://git.example.com/platform/terraform-labels.git`, has no `?ref=`. A pin to a commit SHA or protected tag is needed. I don't know a valid ref, so I left it alone.
- **Module upgrade:** the 6.x VPC module is a new major version. Run `terraform init && terraform validate && terraform plan` in a staging root and read the plan before applying.
