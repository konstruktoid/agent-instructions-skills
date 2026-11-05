The AWS provider is now on 6.x and the VPC is added, but `terraform init` and `validate` did not pass. `terraform fmt -check` is clean, but init can't download the `labels` module because `git.example.com` doesn't resolve from here. Nothing was validated, `tflint` wasn't installed, and no `.terraform.lock.hcl` exists yet.

**What changed**
- `versions.tf`: the AWS provider constraint went from `>= 4.0` to `~> 6.0`. I also added `required_version = ">= 1.10"`.
- `main.tf`: new `module "vpc"` from `terraform-aws-modules/vpc/aws`, pinned to exactly `6.7.3`, with `tags = module.labels.tags`. The provider's `default_tags` still comes from the labels module as before.
- The VPC has two private subnets, one in `eu-north-1a` and one in `eu-north-1b`. NAT is off, so they have no outbound internet route. Say if you want a NAT gateway.
- `variables.tf`: new `vpc_cidr`, `availability_zones` and `private_subnet_cidrs`. The defaults are `10.0.0.0/16`, the two zones, and `10.0.1.0/24` and `10.0.2.0/24`. A validation checks that there is one CIDR per zone. The default CIDRs are placeholders, so change them to your real address plan.
- New `outputs.tf` with `vpc_id` and `private_subnet_ids`, and a new `.gitignore` for state, plan and tfvars files.

**What you need to do**
- Run `terraform init`, `terraform validate` and `tflint` somewhere that can reach the labels repository.
- Commit the `.terraform.lock.hcl` that init produces. Run `terraform providers lock` for each platform your CI uses first.
- Run `terraform plan -out` against staging and read it before any apply. A move from provider 4.x to 6.x can change defaults.
- The VPC name is `network-${var.environment}`. I didn't use a labels output for it because I couldn't read that module's outputs to see what it exposes.

**Existing issue I left alone**
The `labels` module source has no `?ref=`, so it follows the default branch. Pin it to a commit SHA or a protected tag. I don't know which ref is right.
